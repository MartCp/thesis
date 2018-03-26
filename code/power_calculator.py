# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
import json
from pydash import py_
import argparse
from datetime import datetime

import numpy as np

VOLTAGE = 3.3
regex = r"{\"type\":.*?}"

parser = argparse.ArgumentParser(description='NB IoT POWER CALCULATOR')

parser.add_argument('--h', help='help')
parser.add_argument('-f', action='store', dest='file', help='File name', type=str, default='')
parser.add_argument('-s', action='store', dest='start', help='Start time', type=str, default='')
parser.add_argument('-e', action='store', dest='end', help='End time', type=str, default='')

# Parse arguments from user
r = parser.parse_args()

with open(r.file, 'r') as myfile:
	data = myfile.read()

matches = re.finditer(regex, data)

start_index = 0
end_index = 0
result = ""

for matchNum, match in enumerate(matches):
	if matchNum == 8:
		matchNum = matchNum + 1

		result = match.group() + "}"
		user = json.loads(result)

		x_data = user['x']
		y_data = user['y']

		start_index = py_.find_index(x_data, lambda x: r.start in x )
		end_index = py_.find_index(x_data, lambda x: r.end in x )

		measurments = y_data[start_index:end_index]
		avg_a = np.average(measurments)

		start_date = x_data[start_index]
		end_date = x_data[end_index]
		time_usage = (datetime.strptime(end_date, "%Y-%m-%d %H:%M:%S.%f") - datetime.strptime(start_date, "%Y-%m-%d %H:%M:%S.%f")).total_seconds()

		power_usage = round( ( (avg_a * VOLTAGE) / 60 / 60 ) * time_usage, 6 )
		print("From: " + start_date + "\nTo: " + end_date + "\n((" + str(avg_a) + "mA * " + str(VOLTAGE) + "V / 60 / 60 ) * " + str(time_usage) + "S) = " + str(power_usage) + "mWh")


