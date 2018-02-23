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

def do_log( id, delay, release_indicator, modem, nbiot_socket ):
	idx = 1
	while True:
		send_status_command( modem, nbiot_socket, idx, id, release_indicator )
		idx += 1

		sleep(delay)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='NB IoT LABTEST.')

	parser.add_argument('--h', help='help')
	parser.add_argument('-id', action='store', dest='node_id', help='Node id', type=str, default='0')
	parser.add_argument('-d', action='store', dest='delay', help='Set delay', type=int, default=5)
	parser.add_argument('-r', action='store_true', dest='release_indicator', help='Set release_indicator (0-1)')

	# Parse arguments from user
	r = parser.parse_args()

	uart_modem = serial.Serial('/dev/tty.usbserial-146100', 9600, timeout = 0)
	uart_modem.close()
	uart_modem.open()
	uart_modem.flushInput()
	uart_modem.flushOutput()

	startup_command( uart_modem, "AT+NPSMR=1" )

	nbiot_socket = open_socket( uart_modem, 0, 1 )
	do_log( r.node_id, int(r.delay), int(r.release_indicator), uart_modem, nbiot_socket)
