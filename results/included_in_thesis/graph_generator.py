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

plotly.tools.set_credentials_file(username='henninghaakonsen', api_key='ZvGHWo6onbxWo8Zb0hFi')

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

font_size = 26
def get_layout():
	return dict(
		showticklabels=True,
		tickfont=dict(
			size=font_size,
			color='black'
			),
		)

def get_layout_with_title(title):
	return dict(
		title=title,
        titlefont=dict(
            family='Arial, sans-serif',
            size=font_size,
            color='black'
        ),
		showticklabels=True,
		tickfont=dict(
			size=font_size,
			color='black'
			),
		)
def get_basic_layout():
	return dict(
		showticklabels=False,
		)


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

xaxises = {}
yaxises = {}

for matchNum, match in enumerate(matches):
	matchNum = matchNum + 1

	result = match.group(0).split("[", 1)[-1].split("], {\"xaxis1\"", 1)[0]
	result = result.replace("{\"type\"", "\"sec\": {\"type\"")
	result = "{" + result + "}"

	user = json.loads(result, object_pairs_hook=dict_raise_on_duplicates)
	for entry in user:
		if "RECEIVE" in user[entry]['name']:
			rx_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		elif "TRANSMIT" in user[entry]['name']:
			tx_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		elif "TX POWER" in user[entry]['name']:
			tx_pwr_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		elif "COVERAGE" in user[entry]['name']:
			coverage_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		elif "ECL" in user[entry]['name']:
			ecl_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		elif "PSM" in user[entry]['name']:
			psm_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		elif "RRC" in user[entry]['name']:
			con_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		elif "REGISTRATION" in user[entry]['name']:
			reg_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])
		elif "PWR" in user[entry]['name']:
			fluke_trace = go.Scatter(x=user[entry]['x'], y=user[entry]['y'], 
				mode = 'lines', line=user[entry]['line'], name=user[entry]['name'])

fig = None

if r.plot_type == 0:
	fig = tools.make_subplots(rows=12, cols=1,
	                  specs=[
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{'rowspan': 4}],
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
	fig = tools.make_subplots(rows=6, cols=1,
	                  specs=[
	                  			[{}],
	                  			[{}],
	                  			[{'rowspan': 4}],
	                  			[None],
	                  			[None],
	                  			[None],
	                         ],
	                  print_grid=False)

	fig.append_trace(rx_trace, 1, 1)
	fig.append_trace(tx_trace, 2, 1)
	fig.append_trace(fluke_trace, 3, 1)
elif r.plot_type == 2:
	fig = tools.make_subplots(rows=7, cols=1,
	                  specs=[
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{'rowspan': 4}],
	                  			[None],
	                  			[None],
	                  			[None],
	                         ],
	                  print_grid=False)

	fig.append_trace(rx_trace, 1, 1)
	fig.append_trace(tx_trace, 2, 1)
	fig.append_trace(psm_trace, 3, 1)
	fig.append_trace(fluke_trace, 4, 1)
elif r.plot_type == 3:
	fig = tools.make_subplots(rows=8, cols=1,
	                  specs=[
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
	fig.append_trace(fluke_trace, 1, 1)
	
elif r.plot_type == 4:
	fig = tools.make_subplots(rows=7, cols=1,
	                  specs=[
	                  			[{}],
	                  			[{}],
	                  			[{}],
	                  			[{'rowspan': 4}],
	                  			[None],
	                  			[None],
	                  			[None],
	                         ],
	                  print_grid=False)

	fig.append_trace(tx_pwr_trace, 1, 1)
	fig.append_trace(ecl_trace, 2, 1)
	fig.append_trace(coverage_trace, 3, 1)
	fig.append_trace(fluke_trace, 4, 1)


fig_data = [rx_trace, tx_trace, tx_pwr_trace, coverage_trace, ecl_trace, psm_trace, con_trace, reg_trace, fluke_trace]
layout = go.Layout(
	width = 1800,
	height = 1800,
	legend=dict(
		orientation='h',
		font=dict(
            family='sans-serif',
            size=22,
            color='#000'
        ),
	),
    xaxis1=get_layout_with_title('PWR USAGE') if r.plot_type == 3 else get_basic_layout(),
    yaxis1=get_layout(),
    xaxis2=get_basic_layout(),
    yaxis2=get_layout(),
    xaxis3=get_layout() if r.plot_type == 1 else get_basic_layout(),
    yaxis3=get_layout(),
    xaxis4=get_layout() if r.plot_type == 2 else get_basic_layout(),
    yaxis4=get_layout(),
    xaxis5=get_basic_layout(),
    yaxis5=get_layout(),
    xaxis6=get_basic_layout(),
    yaxis6=get_layout(),
    xaxis7=get_basic_layout(),
    yaxis7=get_layout(),
    xaxis8=get_basic_layout(),
    yaxis8=get_layout(),
	xaxis9=get_layout(),
    yaxis9=get_layout(),
)

regex = r"(1000, \"title\": \").*?\""
matches = re.finditer(regex, data)
title = ''
for matchNum, match in enumerate(matches):
	matchNum = matchNum + 1
	title = match.group(0).split("1000, \"title\": \"", 1)[-1][:-1]

fig['layout'].update(layout)
#fig = go.Figure(data = fig_data, layout = layout)

filename = 'short_' + r.file if r.plot_type >= 1 else 'full_' + r.file
py.image.save_as(fig, filename=filename.split('.html', 1)[0].replace('.', '_') + ".jpeg", format='jpeg')


