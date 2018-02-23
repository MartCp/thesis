import json
import requests
import datetime
import random

from time import sleep

count = 0
l = [1, 2, 3]
d = ['node1', 'node2', 'node3']
coverageA = -40
coverageB = -70
coverageC = -90 #+ str(l[2])
#api = 'https://nb-iot-sensorserver.herokuapp.com/'
api = 'http://localhost:8020/'

while True:
	headers = {"Content-Type": "application/x-www-form-urlencoded"}
	
	if count == 5:
		data = {'displayName': d[0], 'type': 'coverage', 'timestamp': datetime.datetime.utcnow().isoformat(), 'coverage': coverageA}
		requests.post(api + 'api/nodes/' + str(l[0]), data=data, headers=headers)

		data = {'displayName': d[1], 'type': 'coverage', 'timestamp': datetime.datetime.utcnow().isoformat(), 'coverage': coverageB}
		requests.post(api + 'api/nodes/' + str(l[1]), data=data, headers=headers)

		data = {'displayName': d[2], 'type': 'coverage', 'timestamp': datetime.datetime.utcnow().isoformat(), 'coverage': coverageC}
		requests.post(api + 'api/nodes/' + str(l[2]), data=data, headers=headers)


		if coverageA <= -120: 
			coverageA = -40
		else: 
			coverageA -= 1

		if coverageB <= -120: 
			coverageB = -40
		else: 
			coverageB -= 1

		if coverageC <= -120: 
			coverageC = -40
		else: 
			coverageC -= 1
		
		count = 0
	else:
		count += 1
		data = {'displayName': d[0], 'type': 'keep-alive', 'timestamp': datetime.datetime.utcnow().isoformat()}
		requests.post(api + 'api/nodes/' + str(l[0]), data=data, headers=headers)

		data = {'displayName': d[1], 'type': 'keep-alive', 'timestamp': datetime.datetime.utcnow().isoformat()}
		requests.post(api + 'api/nodes/' + str(l[1]), data=data, headers=headers)

		data = {'displayName': d[2], 'type': 'keep-alive', 'timestamp': datetime.datetime.utcnow().isoformat()}
		requests.post(api + 'api/nodes/' + str(l[2]), data=data, headers=headers)
	
	sleep(5)
	random.shuffle(l)
