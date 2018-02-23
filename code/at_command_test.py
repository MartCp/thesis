import sys
import serial
import struct
import time

import json
import requests
import datetime
import random
import subprocess

from time import sleep

#api = 'https://nb-iot-sensorserver.herokuapp.com/'
api = 'http://158.39.77.97:9000/'

#uart_conn = serial.Serial('/dev/tty.usbmodem144121', 115200, timeout = 1)
uart_modem = serial.Serial('/dev/tty.usbserial-146100', 9600, timeout = 1)

#uart_conn.close()
uart_modem.close()

#uart_conn.open()
uart_modem.open()

#uart_conn.flushInput()
uart_modem.flushInput()

#uart_conn.flushOutput()
uart_modem.flushOutput()

print uart_modem

counter=0
while True:
	payload = "500230B170112AFF"
	message = raw_input("MESSAGE >")
	command = raw_input("COMMAND >")

	if len(message) > 0:
		command += str((len(payload) / 2) + len(message)) + ",\"" + payload 

		for ch in message:
			command += hex(ord(ch)).upper()[2:]

		command += "\""

	print command
	print uart_modem.write( command + "\r\n" )

	rsp = uart_modem.read(300)
	print "rsp:" + rsp

"""def send_udp(displayName, id):
	headers = {"Content-Type": "application/x-www-form-urlencoded"}

	timestamp = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
	coverage = 0

	data = {'displayName': displayName, 'type': 'coverage', 'timestamp': timestamp, 'coverage': coverage}
	print data
	try:
		requests.post(api + 'api/nodes/' + id, data=data, headers=headers)
	except:
		print "Request post failed" 

def loop(displayName, id):
	line = ""
	try:
		while 1:
			rsp = uart_conn.read()

			if rsp and rsp != "\n":
				line += rsp

			if rsp == "\n":
				if "send" in line:
					send_udp(displayName, id)
				print line
				line = ""
				uart_conn.write('r');
				print ""
				
		uart_conn.close()

	except KeyboardInterrupt:
		print "Program stopped"
		uart_conn.close()
		sys.exit()

if __name__ == "__main__":
    arguments = sys.argv[1:]
    loop(arguments[0], arguments[1])
    """

