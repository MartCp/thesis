# the above tag defines encoding for this document and is for Python 2.x compatibility

import re
import json
from pydash import py_
import argparse
from datetime import datetime
from collections import OrderedDict

import plotly
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go

import numpy as np

def dict_raise_on_duplicates(ordered_pairs):
  count=0
  d={}
  for k,v in ordered_pairs:
      if k in d:
          d[k+'_dupl_'+str(count)]=v
          count+=1
      else:
          d[k]=v
  return d

VOLTAGE = 3.3
regex = r"(<script type=\"text/javascript\">window\.PLOTLYENV=window\.PLOTLYENV.*?\[).*?(\], {\"xaxis1\")"

parser = argparse.ArgumentParser(description='NB IoT POWER CALCULATOR')

parser.add_argument('--h', help='help')
parser.add_argument('-f', action='store', dest='file', help='File name', type=str, default='')
parser.add_argument('-pt', action='store', dest='plot_type', help='Select plot type', type=int, default=0)

# Parse arguments from user
r = parser.parse_args()

with open(r.file, 'r') as myfile:
	data = myfile.read()

matches = re.finditer(regex, data)

start_index = 0
end_index = 0
result = ""

rx_trace = None
tx_trace = None
tx_pwr_trace = None
coverage_trace = None
ecl_trace = None
psm_trace = None
con_trace = None
reg_trace = None
fluke_trace = None

lines = {
'rx': dict(
	shape='spline', 
	color=('red')), 
'tx': dict(
	shape='spline', 
	color=('blue')), 
'tx_pwr': dict(
	shape='hv',
	color=('black')),
'coverage': dict(
	shape='spline',
	color=('purple')), 
'ecl': dict(
	shape='hv',
	color=('magenta')), 
'psm': dict(
	shape='hv',
	color=('rgb(0, 0, 255)')), 
'con': dict(
	shape='hv',
	color=('rgb(204, 204, 0)')), 
'reg': dict(
	shape='hv',
	color=('green'))
}


for matchNum, match in enumerate(matches):
	matchNum = matchNum + 1

	result = match.group(0).split("[", 1)[-1].split("], {\"xaxis1\"", 1)[0]
	result = result.replace("{\"type\"", "\"sec\": {\"type\"")
	result = "{" + result + "}"

	user = json.loads(result, object_pairs_hook=dict_raise_on_duplicates)
	for entry in user:
		if "RECEIVE" in user[entry]['name']:
			rx_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		if "TRANSMIT" in user[entry]['name']:
			tx_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		if "TX POWER" in user[entry]['name']:
			tx_pwr_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		if "COVERAGE" in user[entry]['name']:
			coverage_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		if "ECL" in user[entry]['name']:
			ecl_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		if "PSM" in user[entry]['name']:
			psm_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		if "RRC" in user[entry]['name']:
			con_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		if "REGISTRATION" in user[entry]['name']:
			reg_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		if "PWR" in user[entry]['name']:
			fluke_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		

fig = None

if r.plot_type == 0:
	fig = tools.make_subplots(rows=16, cols=1,
	                  specs=[
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{'rowspan': 8}],
	                  			[None],
	                  			[None],
	                  			[None],
	                  			[None],
	                  			[None],
	                  			[None],
	                  			[None],
	                         ],
	                  print_grid=False)

	fig.append_trace(rx_trace, 1, 1)
	fig.append_trace(tx_trace, 2, 1)
	fig.append_trace(tx_pwr_trace, 3, 1)
	fig.append_trace(coverage_trace, 4, 1)
	fig.append_trace(ecl_trace, 5, 1)
	fig.append_trace(psm_trace, 6, 1)
	fig.append_trace(con_trace, 7, 1)
	fig.append_trace(reg_trace, 8, 1)
	fig.append_trace(fluke_trace, 9, 1)
elif r.plot_type == 1:
	fig = tools.make_subplots(rows=10, cols=1,
	                  specs=[
	                  			[{}],
	                  			[{}],
	                  			[{'rowspan': 8}],
	                  			[None],
	                  			[None],
	                  			[None],
	                  			[None],
	                  			[None],
	                  			[None],
	                  			[None],
	                         ],
	                  print_grid=False)

	fig.append_trace(rx_trace, 1, 1)
	fig.append_trace(tx_trace, 2, 1)
	fig.append_trace(fluke_trace, 3, 1)

regex = r"(1000, \"title\": \").*?\""
matches = re.finditer(regex, data)
title = ''
for matchNum, match in enumerate(matches):
	matchNum = matchNum + 1
	title = match.group(0).split("1000, \"title\": \"", 1)[-1][:-1]

fig['layout'].update(width = 1800, height = 1800, title = title)

filename = 'short_' + r.file if r.plot_type == 1 else 'full_' + r.file
plotly.offline.plot(fig, filename=filename)


