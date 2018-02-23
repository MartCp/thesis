import json
import requests
import datetime
import random
import sys
import subprocess

from time import sleep

#api = 'https://nb-iot-sensorserver.herokuapp.com/'
api = 'http://158.39.77.97:9000/'
#api = 'http://localhost:8020/'


def loop(displayName, id):
    count = 0

    while True:
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
        if count == 5:
            lines = subprocess.Popen("airport -I", shell=True, stdout=subprocess.PIPE).communicate()[0]
            coverage = lines.splitlines()[0].split(" ")[6]

            data = {'displayName': displayName, 'type': 'coverage', 'timestamp': timestamp, 'coverage': coverage}
            requests.post(api + 'api/nodes/' + id, data=data, headers=headers)

            count = 0
        else:
            count += 1
            data = {'displayName': displayName, 'type': 'keep-alive', 'timestamp': timestamp}
            requests.post(api + 'api/nodes/' + id, data=data, headers=headers)

        sleep(5)


arguments = sys.argv[1:]
loop(arguments[0], arguments[1])
