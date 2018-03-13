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

import signal

api = 'http://158.39.77.97:9000/'
HOST, PORT = '10.0.1.2', 3490
VOLTAGE = 3.3

date_points = []

coverage_points = []
ecl_points = []
rx_points = []

tx_points = []
tx_pwr_points = []

psm_points = []
cscon_points = []
cereg_points = []

print_graph = False

def signal_handler(signal, frame):
	print('You pressed Ctrl+C... generating graphs')
	global print_graph

	print_graph = True

def do_log( modem, prev_time, prev_rx_val, prev_tx_val ):
	rx_point = 0
	tx_point = 0
	tx_pwr_point = 0
	psm_point = 0
	cscon_point = 0
	coverage_point = 0
	ecl_point = 0
	cereg_point = 0

	nuestats_list = get_nuestats( modem )

	if len(nuestats_list) > 10:
		time_val = datetime.datetime.now()
		interval = ( time_val - prev_time ).total_seconds()

		coverage_point = int (nuestats_list[0]) / 10
		tx_pwr_point = int (nuestats_list[2]) / 10
		tx_val = int (nuestats_list[3])
		rx_val = int (nuestats_list[4])
		ecl_point = int (nuestats_list[6])

		psm_point =  get_npsmr( modem )
		cscon_point = get_cscon( modem )
		cereg_point = get_cereg( modem ) 

		if prev_rx_val != 0:
			rx_time = ( rx_val - prev_rx_val )
			rx_result = rx_time / ( interval * 1000 )
			rx_point = rx_result

			tx_time = ( tx_val - prev_tx_val )
			tx_result = tx_time / ( interval * 1000 )
			tx_point = tx_result

		prev_time = time_val
		prev_rx_val = rx_val
		prev_tx_val = tx_val
	else:
		startup( modem )

		socket = open_socket( modem, 0, 1 )

	date_points.append( time_val.strftime("%Y-%m-%d %H:%M:%S.%f") )

	rx_points.append( rx_point )
	tx_points.append( tx_point )
	tx_pwr_points.append( tx_pwr_point )
	psm_points.append( psm_point )
	cscon_points.append( cscon_point )
	coverage_points.append( coverage_point )
	ecl_points.append( ecl_point )
	cereg_points.append( cereg_point )

	return prev_time, prev_rx_val, prev_tx_val

def send(modem, nbiot_socket, idx, id, release, nr_bytes):
	if nr_bytes is not 0:
		sendToXBytes( modem, nr_bytes, nbiot_socket, id, release)
	else:
		send_status_command( modem, nbiot_socket, idx, id, release )

def loop(id, graph_name, delay, iterations, nr_bytes, release, logging, modem, fluke_socket, nbiot_socket, reboot):
	idx = 0
	prev_rx_val = 0
	prev_tx_val = 0
	prev_do_fluke = 0

	fluke_points = []

	signal.signal(signal.SIGINT, signal_handler)

	global date_points
	global coverage_points
	global ecl_points
	global rx_points
	global tx_points
	global tx_pwr_points
	global psm_points
	global cscon_points
	global cereg_points

	date_points = []
	coverage_points = []
	ecl_points = []
	rx_points = []
	tx_points = []
	tx_pwr_points = []
	psm_points = []
	cscon_points = []
	cereg_points = []

	start = time()
	start_timer = time()
	idx = 1
	
	prev_time = datetime.datetime.now()

	prev_time, prev_rx_val, prev_tx_val = do_log( modem, prev_time, prev_rx_val, prev_tx_val)
	send_and_receive_fluke( fluke_socket, ":INIT")
	if reboot:
		startup_command( uart_modem, "AT+NRB" )
	else:
		send(modem, nbiot_socket, idx, id, release, nr_bytes)

	start_point = datetime.datetime.now()

	print( "start logging(" + str(logging) + ")")
	while True:
		if logging is 1:
			prev_time, prev_rx_val, prev_tx_val = do_log( modem, prev_time, prev_rx_val, prev_tx_val)
		
		if logging is 0:
			sleep(2)

		do_fluke = math.ceil( int( time() - start ) )
		if do_fluke % 5 is 0 and do_fluke is not prev_do_fluke:
			fluke_points.extend( handle_fluke_reading( fluke_socket ) )
			prev_do_fluke = do_fluke

		if int( time() - start ) >= delay:
			if idx == iterations and iterations != -1:
				break

			idx += 1

			send(modem, nbiot_socket, idx, id, release, nr_bytes)
			start = time()

		if print_graph:
			break
		
	fluke_points.extend( handle_fluke_reading( fluke_socket ) )

	end_point = datetime.datetime.now()
	time_usage = time() - start_timer

	rx_points = remove_bad_data(rx_points, 0, 5)
	rx_trace = 			go.Scatter(x=date_points, y=rx_points, mode = 'lines', line=dict(
																				        shape='spline',
																				        color=('red'),
																				    ), name='RECEIVE (%)')
	tx_points = remove_bad_data(tx_points, 0, 5)
	tx_trace = 			go.Scatter(x=date_points, y=tx_points, mode = 'lines', line=dict(
																				        shape='spline',
																				        color=('blue'),
																				    ), name='TRANSMIT (%)')

	tx_pwr_points = remove_bad_data(tx_pwr_points, -40, 30)
	tx_pwr_trace = 		go.Scatter(x=date_points, y=tx_pwr_points, mode = 'lines', line=dict(
																				        shape='hv',
																				        color=('black'),
																				    ), name='TX POWER (dBm)')
	coverage_points = remove_bad_data(coverage_points, -150, 0)
	coverage_trace = 	go.Scatter(x=date_points, y=coverage_points, mode = 'lines', line=dict(
																				        shape='spline',
																				        color=('purple'),
																				    ), name='COVERAGE (dBm)')
	ecl_trace = 		go.Scatter(x=date_points, y=ecl_points, mode = 'lines', line=dict(
																			        	shape='hv',
																				        color=('magenta'),
																			        ), name='ECL LEVEL (0-3)')
	psm_trace = 		go.Scatter(x=date_points, y=psm_points, mode = 'lines', line=dict(
																			        	shape='hv',
																				        color=('rgb(0, 0, 255)'),
																			        ), name='PSM (0-1)')
	con_trace = 		go.Scatter(x=date_points, y=cscon_points, mode = 'lines', line=dict(
																			        	shape='hv',
																				        color=('rgb(204, 204, 0)'),
																			        ), name='RRC STATE (0-1)')
	reg_trace = 		go.Scatter(x=date_points, y=cereg_points, mode = 'lines', line=dict(
																			        	shape='hv',
																				        color=('green'),
																			        ), name='REGISTRATION STATUS (0-5)')

	fluke_points = list( map(remove_high_convert_to_ma, fluke_points) )
	fluke_points = list( filter( None, fluke_points) )
	fluke_len = len( fluke_points )
	print(fluke_len)
	avg_a = np.mean( fluke_points )

	time_diff = end_point - start_point
	interval = int( time_diff.total_seconds() * 1000000 / fluke_len )

	fluke_range = []
	temp_date = start_point
	while temp_date <= end_point:
		fluke_range.append( temp_date.strftime("%Y-%m-%d %H:%M:%S.%f") )
		temp_date = temp_date + datetime.timedelta(microseconds=interval)
	
	fluke_trace = 		go.Scatter(x=fluke_range, y=fluke_points, mode = 'lines', line=dict(
																				        shape='spline',
																				        color=('rgb(0, 153, 255)'),
																				    ), name='PWR USAGE (mA)')

	fig = tools.make_subplots(rows=8, cols=2,
                          specs=[
                          			[{}, {'rowspan': 8}],
                          			[{}, None],
                          			[{}, None],
                          			[{}, None],
                          			[{}, None],
                          			[{}, None],
                          			[{}, None],
                          			[{}, None],
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
	fig.append_trace(fluke_trace, 1, 2)

	flag = "0x0"
	if release is 1:
		flag = "0x2"

	logging_string = ""
	if logging is 0:
		logging_string = " NO DEVICE LOGGING "

	filename = graph_name + " " + str(datetime.date.today()) + " " + str(logging) + " " + flag + " " + str(delay) + " " +  str(idx) + " " + str(nr_bytes)
	power_usage = round( ( (avg_a * VOLTAGE) / 60 / 60 ) * time_usage, 6 )
	graph_name += " " + str(datetime.date.today()) + " " + logging_string + flag + " " + str(delay) + " SEC " + str(idx) + " INTERVALS (TIME USED: " + str(int(time_usage)) +  "S ) " + str(nr_bytes) + " BYTES - AVERAGE LOAD " + str( avg_a ) + "mA, POWER USAGE " + str( power_usage ) + "mWh"
	fig['layout'].update(width = 1800, height = 1000, title = graph_name)

	plotly.offline.plot(fig, filename=filename.replace(" ", "_") + ".html")

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='NB IoT LABTEST.')

	parser.add_argument('--h', help='help')
	parser.add_argument('-id', action='store', dest='node_id', help='Node id', type=str, default=0)
	parser.add_argument('-gn', action='store', dest='graph_name', help='Graph name')
	parser.add_argument('-d', action='store', dest='delay', help='Set delay', type=int, default=5)
	parser.add_argument('-i', action='store', dest='iterations', help='Set iterations', type=int, default=-1)
	parser.add_argument('-b', action='store', dest='nr_bytes', help='Set nr bytes (0 equals send NUESTATS)', type=int, default=-1)
	parser.add_argument('-r', action='store_true', dest='release_indicator', help='Set release_indicator (0-1)')
	parser.add_argument('-l', action='store_true', dest='logging', help='Set device logging')
	parser.add_argument('-rb', action='store_true', dest='reboot', help='Set reboot test')

	# Parse arguments from user
	r = parser.parse_args()

	fluke_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	fluke_socket.settimeout(15)
	fluke_socket.connect((HOST, PORT))

	uart_modem = serial.Serial('/dev/tty.usbserial-146100', 9600, timeout = 0)
	uart_modem.close()
	uart_modem.open()
	uart_modem.flushInput()
	uart_modem.flushOutput()

	startup( uart_modem )
	#startup_command( uart_modem, "AT+NPSMR=1" )
	nbiot_socket = open_socket( uart_modem, 0, 1 )

	if r.reboot:
		loop(0, r.graph_name, int(r.delay), int(r.iterations), 0, 0, int(r.logging), uart_modem, fluke_socket, nbiot_socket, r.reboot)
	else:
		keys = [100]#, 50, 200, 512]

		for key in keys:
			loop(r.node_id, r.graph_name, int(r.delay), int(r.iterations), key, 0, 0, uart_modem, fluke_socket, nbiot_socket, r.reboot)
			loop(r.node_id, r.graph_name, int(r.delay), int(r.iterations), key, 1, 0, uart_modem, fluke_socket, nbiot_socket, r.reboot)
			loop(r.node_id, r.graph_name, int(r.delay), int(r.iterations), key, 0, 1, uart_modem, fluke_socket, nbiot_socket, r.reboot)
			loop(r.node_id, r.graph_name, int(r.delay), int(r.iterations), key, 1, 1, uart_modem, fluke_socket, nbiot_socket, r.reboot)

	fluke_socket.close()

	close_socket( uart_modem, nbiot_socket )
	sys.exit()

