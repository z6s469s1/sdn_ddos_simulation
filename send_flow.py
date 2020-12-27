import os
import argparse
from scapy.all import *


parser = argparse.ArgumentParser()
parser.add_argument('--input_path', '-i', type=str, required=True, help='input path')
parser.add_argument('--nic', '-n', type=str, required=True, help='nic')
parser.add_argument('--not_filter_large_pk', '-f', required=False, help='not_filter_large_pk',action='store_false',default=True)
parser.add_argument('--max_pk_len', '-m', type=int, required=False, help='max_pk_len',default=1506)


args = parser.parse_args()
input_path=args.input_path
send_nic=args.nic
max_pk_len=args.max_pk_len
not_filter_large_pk=args.not_filter_large_pk

pcap_names=os.listdir(input_path)

for pcap_name in pcap_names:
    
    if not_filter_large_pk:
        pcap = rdpcap(input_path+pcap_name)
        max_len=0
        for pk in pcap:
            if len(pk) > max_len:
                max_len=len(pk)

        if max_len>max_pk_len:
            continue

    print("-"*70)
    #cmd="sudo bittwist -i "+send_nic+" "+input_path+pcap_name
    cmd="sudo bittwist -i "+send_nic+" "+input_path+pcap_name+"  -r 5"
    os.system(cmd)
    print("-"*70)

