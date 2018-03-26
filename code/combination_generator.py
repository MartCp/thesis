# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
from pydash import py_
import argparse

import numpy as np

VOLTAGE = 3.3

regex = r"\"title\": \".*?\""

parser = argparse.ArgumentParser(description='NB IoT LABTEST.')

parser.add_argument('--h', help='help')
parser.add_argument('-p', action='store', dest='parse', help='File name parse string', type=str, default='')
parser.add_argument('-d', action='store', dest='dir', help='Directory', type=str, default='.')


# Parse arguments from user
r = parser.parse_args()

combinations = {}

import os
for dir in os.listdir(r.dir):
	if "precision" in dir and ".html" in dir and r.parse in dir:
		data = ""
		with open(r.dir + dir, 'r') as myfile:
			data = myfile.read()

		matches = re.finditer(regex, data)

		title = ""

		for matchNum, match in enumerate(matches):
			matchNum = matchNum + 1

			title = match.group()

			titleList = title.split(' ')
			if len(titleList) < 15:
				continue


			flag_str = titleList[ py_.find_index(titleList, lambda x: "x" in x ) ]

			flag = 0
			if "2" in flag_str:
				flag = 1

			location = titleList[1]
			network = titleList[2]
			dbm = titleList[5]
			if "dBm" not in dbm:
				dbm = "0dbm"

			sec = py_.find_index(titleList, lambda x: "SEC" in x )
			delay = titleList[ sec - 1]
			iterations = titleList[ sec + 1]

			nr_bytes = titleList[ py_.find_index(titleList, lambda x: "BYTES" in x ) - 1 ]
			avg_ma = titleList[ py_.find_index(titleList, lambda x: "LOAD" in x ) + 1][:-3]
			power_usage = titleList[ py_.find_index(titleList, lambda x: "USAGE" in x ) + 1][:-4]

			time_usage = int(delay) * int(iterations)

			key = dbm + "_" + network + "_" + str(delay) + "_" + str(iterations) + "_" + str(flag) + "_" + str(nr_bytes)
			
			entry = [float(avg_ma), float(power_usage)]
			if key in combinations:
				combinations[key].append( entry )
			else:
				combinations[key] = [entry]

for key in combinations:
	a = np.array(combinations[key])
	print(key + ": " + str(a.mean(axis=0)))
