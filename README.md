# SDN Final
[SDN期末報告:DDOS實驗數據與實驗影片](https://hackmd.io/97zjY1qVS1W7P4y4tFXD0w)


## Start onos controller

```sh
# start onos with docker or whatever you want
sudo docker run --rm -t -d -p 8101:8101 -p 8181:8181 -p 9876:9876 -p 6653:6653 -p 6640:6640 --name onos onosproject/onos

# install sshpass for following command:
sudo apt install sshpass

# config onos
sshpass -p rocks ssh -p 8101 -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null onos@localhost "feature:install onos-providers-openflow-app; feature:install onos-providers-openflow-message; app activate org.onosproject.fwd; app activate org.onosproject.openflow"

curl -s --user onos:rocks -H 'Content-Type: application/json' http://localhost:8181/onos/v1/configuration/org.onosproject.fwd.ReactiveForwarding -d '{ "matchIpv4Address": "true", "flowTimeout": "600"}'
```

**UI**: http://localhost:8181/onos/ui/

## Start mininet
```sh
sudo -H python TreeTopo.py
pingall
```
## Start detect DDoS
```sh
# install required python packages
python3 -m venv venv
. ./venv/bin/activate
pip install --pre scapy[basic]
pip install -U scikit-learn requests

# switch to root to start detect
sudo -H -s
. ./venv/bin/activate
./main.py
```

After start main.py, please wait for 5 seconds to collect normal flows


## Start DDoS
```sh
# open terminal for hosts from mininet
# it's okay to use other terminal
mininet>
h1 qterminal &
h2 qterminal &
h3 qterminal &
h4 qterminal &

# choose one host as victim, take h1 for example:
user@h1 #
python -m SimpleHTTPServer 8000



# send normal flow and calulate RTT
# choose hosts send TCP request to the victim
user@h2
python3 client_request.py http://10.0.0.1:8000/index.html 0.5 100 2


# choose  attckers
user@h3
hping3 -c 10000 -d 120 -S -w 64 -p 21 --flood  10.0.0.1 -p 8000
user@h4
hping3 -c 10000 -d 120 -S -w 64 -p 21 --flood  10.0.0.1 -p 8000


# now check the output from main.py
```

## Reference
- Distributed Denial of Service Defense in Software Defined Network Using OpenFlow
