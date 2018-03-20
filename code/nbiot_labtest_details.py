import sys
import serial
import socket
import struct
from time import *
import argparse

import pandas

import json
import datetime
import random
import subprocess

from nbiot_helpers import *
from decimal import Decimal
import math
import numpy as np

import plotly
from plotly import tools
import plotly.plotly as py
import plotly.graph_objs as go

api = 'http://158.39.77.97:9000/'
HOST, PORT = '10.0.1.2', 3490
VOLTAGE = 3.3

keys = ['25', '50', '100', '200', '400', '512']
results = {key: [] for key in keys}
traces = {key: None for key in keys}

def generate_scatter( points, function ):
	result = []
	if function is 'average':
		result = list( map(lambda x: np.average(points[x]), points) )
	elif function is 'sum':
		result = list( map(lambda x: np.sum(points[x]), points) )
	elif function is 'min':
		result = list( map(lambda x: np.min(points[x]), points) )
	elif function is 'max':
		result = list( map(lambda x: np.max(points[x]), points) )

	return go.Scatter(x=list( keys ), y=result, mode = 'lines', line=dict(
																       shape='spline',
																    ), 
																name=function + " (mWh)")

def do_log( graph_name, delay, iterations, release_indicator, modem, fluke_socket, nbiot_socket ):
	sendToXBytes( modem, 10, nbiot_socket, 0, 1)
	sleep(10)

	for x in range(0, iterations):
		for key in keys:
			fluke_reading = []
			prev_do_fluke = 0

			send_and_receive_fluke( fluke_socket, ":INIT")
			start = time()

			sendToXBytes( modem, int(key), nbiot_socket, 0, release_indicator)
			while True:
				do_fluke = math.ceil( int( time() - start ) )
				if do_fluke % 2 is 0 and do_fluke is not prev_do_fluke:
					fluke_reading.extend( handle_fluke_reading( fluke_socket ) )
					prev_do_fluke = do_fluke

				if int( time() - start ) >= delay:
					break
			
			time_usage = time() - start
			fluke_reading.extend( handle_fluke_reading( fluke_socket ) )

			fluke_reading = list( map(remove_high_convert_to_ma, fluke_reading) )
			fluke_reading = list( filter( None, fluke_reading) )

			avg_a = np.mean( fluke_reading )
			power_usage = round( ( (avg_a * VOLTAGE) / 60 / 60 ) * time_usage, 6 )

			results[key].append( power_usage )
			print(results[key], avg_a, time_usage, round( ( (avg_a * VOLTAGE) / 60 / 60 ) * time_usage, 6 ))
			sleep(10)
	
	for key in keys:
		traces[key] = go.Scatter(x=list( range(1, iterations+1) ), y=results[key], mode = 'lines', line=dict(
																				       shape='spline',
																				    ), name=key + "B (mWh)")


	traces['average'] = generate_scatter( results, 'average')
	traces['sum'] = generate_scatter( results, 'sum')
	traces['min'] = generate_scatter( results, 'min')
	traces['max'] = generate_scatter( results, 'max')
	fig = tools.make_subplots(rows=1, cols=2,
                          specs=[
                          			[{}, {}],
                                 ],
                          print_grid=False)

	fig.append_trace(traces['25'], 1, 1)
	fig.append_trace(traces['50'], 1, 1)
	fig.append_trace(traces['100'], 1, 1)
	fig.append_trace(traces['200'], 1, 1)
	fig.append_trace(traces['400'], 1, 1)
	fig.append_trace(traces['512'], 1, 1)
	fig.append_trace(traces['average'], 1, 2)
	fig.append_trace(traces['sum'], 1, 2)
	fig.append_trace(traces['min'], 1, 2)
	fig.append_trace(traces['max'], 1, 2)

	flag = "0x0"
	if release_indicator is 1:
		flag = "0x2"

	filename = graph_name + " " + str(datetime.date.today()) + " " + flag + " " + str(delay) + " " +  str(iterations)
	graph_name += " " + str(datetime.date.today()) + " " + flag + " " + str(delay) + " SEC " + str(iterations) + " INTERVALS"
	fig['layout'].update(width = 1800, height = 1000, title = graph_name)
	fig['layout']['yaxis1'].update(title='mWh')
	fig['layout']['xaxis1'].update(title='Sample', tickformat=',d')
	fig['layout']['yaxis2'].update(title='mWh')
	fig['layout']['xaxis2'].update(title='Bytes sent')
	
	plotly.offline.plot(fig, filename=filename.replace(" ", "_") + ".html")

	fluke_socket.close()

	close_socket( modem, nbiot_socket )
	sys.exit()

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='NB IoT LABTEST.')

	parser.add_argument('--h', help='help')
	parser.add_argument('-gn', action='store', dest='graph_name', help='Graph name')
	parser.add_argument('-d', action='store', dest='delay', help='Set delay', type=int, default=5)
	parser.add_argument('-i', action='store', dest='iterations', help='Set iterations', type=int, default=1)
	parser.add_argument('-r', action='store_true', dest='release_indicator', help='Set release_indicator (0-1)')

	# Parse arguments from user
	r = parser.parse_args()

	fluke_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	fluke_socket.settimeout(15)
	fluke_socket.connect((HOST, PORT))

	uart_modem = serial.Serial('/dev/tty.usbserial-144100', 9600, timeout = 0)
	uart_modem.close()
	uart_modem.open()
	uart_modem.flushInput()
	uart_modem.flushOutput()

	startup_command( uart_modem, "AT+NPSMR=1" )

	nbiot_socket = open_socket( uart_modem, 0, 1 )
	do_log( r.graph_name, int(r.delay), int(r.iterations), int(r.release_indicator), uart_modem, fluke_socket, nbiot_socket)
