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

api = 'http://158.39.77.97:9000/'

uart_modem = serial.Serial('/dev/tty.usbserial-146100', 9600, timeout = 1)

uart_modem.close()
uart_modem.open()
uart_modem.flushInput()
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

