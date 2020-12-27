import time
import requests
import sys
import statistics


def find_roundtriptime(url,interrupt_time):
      isTimeout=False
      initial_time = time.time() #Store the time when request is sent
      try:
            request = requests.get(url,timeout=interrupt_time, verify=False)
      except:
            isTimeout=True
      ending_time = time.time() #Time when acknowledged the request
      
      return ending_time - initial_time,isTimeout


url=sys.argv[1]
interval_time=float(sys.argv[2])
num_send_request=int(sys.argv[3])
interrupt_time=float(sys.argv[4])

rtt_list=[]
t_s=time.time()
while True:
      if time.time()-t_s > interval_time:

            
            elapsed_time,isTimeout = find_roundtriptime(url,interrupt_time)
            rtt_list.append(elapsed_time)
            
            if isTimeout or elapsed_time>interrupt_time:
                  print('-'*80)
                  print("TIMEOUT!")
            print('[{}]: The Round Trip Time for {} is {}'.format(len(rtt_list),url, elapsed_time))
            if isTimeout or elapsed_time>interrupt_time:
                  print('-'*80)
      
            if len(rtt_list)==num_send_request:
                  break

            t_s=time.time()


print("num of sessions:"+str(len(rtt_list)))
print("mean:"+str(statistics.mean(rtt_list)))
print("var:"+str(statistics.variance(rtt_list)))
print("max:"+str(max(rtt_list)))
print("min:"+str(min(rtt_list)))
