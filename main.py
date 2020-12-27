#!/usr/bin/env python3
import threading, time, math, itertools, json
from collections import Counter
from scapy.all import sniff, AsyncSniffer, IP, TCP, UDP
from sklearn.cluster import KMeans
import numpy as np
import requests

MAX_WINDOW_SIZE = 5
TIME_INTERVAL = 1 # 1 second per window
drop_template = open('drop_src.json').read().replace('{', '{{').replace('}', '}}').replace('{{device_id}}', '{device_id}').replace('{{ip}}', '{ip}')
white_list=["10.0.0.1"]

class set_interval:
    def __init__(self, func, sec):
        self.func = func
        self.sec = sec
        self.create_timer()

    def create_timer(self):
        def func_wrapper():
            self.create_timer()
            self.func()
        self.current = threading.Timer(self.sec, func_wrapper)
        self.current.start()

    def cancel(self):
        self.current.cancel()

windows = {}
def f(pkt):
    # print(pkt.fields)
    # print(pkt.direction)
    # print(pkt.name)
    # print(pkt.original)
    # print(pkt.sent_time)
    # print(pkt.sniffed_on)
    # print(pkt.time)
    # print(pkt.summary())
    # if TCP in pkt and IP in pkt:
    if IP in pkt:
        # tcp_sport = pkt[TCP].sport
        # tcp_dport = pkt[TCP].dport
        ip_src = pkt[IP].src
        ip_dst = pkt[IP].dst
        windows.setdefault(int(pkt.time / TIME_INTERVAL), []).append({
            'ip_dst': ip_dst,
            'ip_src': ip_src,
        })
    # print(windows)
# sniff(count=2, iface='es1-eth1', prn=f)
sniffer = AsyncSniffer(iface=['es1-eth1', 'es1-eth2', 'es2-eth1', 'es2-eth2', 'es3-eth1', 'es3-eth2', 'es4-eth1', 'es4-eth2'], prn=f, filter="ip")
sniffer.start()

last_window_index = -1
Qs = [[] for _ in range(MAX_WINDOW_SIZE)]
Hs = [0 for _ in range(MAX_WINDOW_SIZE)]
Ws = [0]
Ws_ = [0]
buf_ip_srcs = []
count = 0
def f():
    global last_window_index, Qs, Hs, Ws, Ws_, buf_ip_srcs, count
    now = time.time()
    current_window_index = int(now / TIME_INTERVAL) % MAX_WINDOW_SIZE
    if last_window_index == -1:
        last_window_index = current_window_index
    if last_window_index != current_window_index:
        last_window_index = current_window_index
        x = windows.get(int(now / TIME_INTERVAL)-1, [])
        if int(now / TIME_INTERVAL)-1 in windows:
            del windows[int(now / TIME_INTERVAL)-1]
        ip_src = list(map(lambda x: x['ip_src'], x))
        ip_dst = list(map(lambda x: x['ip_dst'], x))
        buf_ip_srcs.append(ip_src)
        if len(buf_ip_srcs) > MAX_WINDOW_SIZE: buf_ip_srcs.pop(0)
        x = Counter(ip_dst)
        Q = [1]
        if sum(x.values()) != 0:
            Nall = sum(x.values())
            Q = [Ni / Nall for Ni in x.values()]
            print(Q)
        Qs[current_window_index-1] = Q
        alpha = 8
        H = 1/(1-alpha) * math.log2(sum([qi ** alpha for qi in Q]))
        Hs[current_window_index-1] = H
        # print('H:', H)
        delta = 0.9
        W = delta * Ws[-1] + (1-delta) * H
        Ws.append(W)
        if len(Ws) > MAX_WINDOW_SIZE: Ws.pop(0)
        W_ = 9 / 10 * W
        Ws_.append(W_)
        if len(Ws_) > MAX_WINDOW_SIZE: Ws_.pop(0)
        # if the entropy value of the current window is less than the window threshold
        # H > 0.01 because no traffic H is 0
        # then it is DDoS
        if H < W_ and len(ip_dst) > 20:
        #if H < W_ and abs(H) > 1e-9:
            count += 1
            print('count:', count)
        else:
            count = 0
        print(f'entropy value H: {H}, threshold W_: {W_}')
        if count >= 5:
            count = 0
            print('DDoS detected')
            ips = list(itertools.chain(*buf_ip_srcs))
            x = []
            x_ip = []
            for ip in set(ips):
                n = Counter(ips)[ip]
                m = len(list(filter(lambda x: ip in x, buf_ip_srcs)))
                wind = list(filter(lambda x: ip in x[1], enumerate(buf_ip_srcs)))
                Ns = wind[0][0]
                Ne = wind[-1][0]
                delta_t = TIME_INTERVAL
                # print(f'R_{ip} = {-Ws[0]} * {n} - {Ws[1]} * {m} + {Ws[2]} * ({Ne} - {Ns} + 1) * {delta_t} / {n}')
                R = -Ws[0] * n - Ws[1] * m + Ws[2] * (Ne - Ns + 1) * delta_t / n
                x.append([R])
                x_ip.append(ip)
                print(f'R_{ip} = {R}')

            if len(x)>0:
                
                kmeans = KMeans(n_clusters=2, random_state=0).fit(x)
                abnormal_label = kmeans.labels_[np.argmin(x)]
                black_list = np.array(x_ip)[kmeans.labels_ == abnormal_label]
                print('black_list:', black_list)
                    
                for ip in black_list:
                    if ip in white_list:
                        continue
                    for device_id in ['of:0000000000000400', 'of:0000000000000500', 'of:0000000000000600', 'of:0000000000000700']:
                        requests.post('http://localhost:8181/onos/v1/flows/'+device_id,
                                auth=('onos', 'rocks'),
                                json=json.loads(drop_template.format(device_id=device_id, ip=ip)))
                
    # print('windows:', windows)
    return

set_interval(f, 1)
