# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
from pydash import py_
import argparse

VOLTAGE = 3.3

regex = r"\"title\": \".*?\""

parser = argparse.ArgumentParser(description='NB IoT LABTEST.')

parser.add_argument('--h', help='help')
parser.add_argument('-p', action='store', dest='parse', help='File name parse string', type=str, default='')

# Parse arguments from user
r = parser.parse_args()

import os
for dir in os.listdir("."):
	if "precision" in dir and ".html" in dir and r.parse in dir:
		data = ""
		with open(dir, 'r') as myfile:
			data = myfile.read()

		matches = re.finditer(regex, data)

		title = ""

		for matchNum, match in enumerate(matches):
			matchNum = matchNum + 1

			title = match.group()

			titleList = title.split(' ')
			if len(titleList) < 15:
				continue
			print(titleList)

			flag_str = titleList[ py_.find_index(titleList, lambda x: "x" in x ) ]

			flag = 0
			if "2" in flag_str:
				flag = 1

			sec = py_.find_index(titleList, lambda x: "SEC" in x )
			delay = titleList[ sec - 1]
			iterations = titleList[ sec + 1]

			nr_bytes = titleList[ py_.find_index(titleList, lambda x: "BYTES" in x ) - 1 ]
			avg_ma = titleList[ py_.find_index(titleList, lambda x: "LOAD" in x ) + 1][:-3]
			power_usage = titleList[ py_.find_index(titleList, lambda x: "USAGE" in x ) + 1][:-4]

			time_usage = int(delay) * int(iterations)

			print(flag, delay, iterations, nr_bytes, avg_ma, power_usage)
