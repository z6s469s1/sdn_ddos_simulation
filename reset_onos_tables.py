#!/usr/bin/env python3
import requests
x = requests.get('http://localhost:8181/onos/v1/flows', auth=('onos', 'rocks'))
added_by_rest = map(lambda x: (x['deviceId'], x['id']), filter(lambda x: x['appId'] == 'org.onosproject.rest',x.json()['flows']))
for device_id, id_ in added_by_rest:
    requests.delete(f'http://localhost:8181/onos/v1/flows/{device_id}/{id_}', auth=('onos', 'rocks'))
