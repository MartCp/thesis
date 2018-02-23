from nuestats_helpers import *
import matplotlib.pyplot as plt
import math
import sys
import socket
import serial

HOST, PORT = '192.168.1.2', 3490

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(15)
sock.connect((HOST, PORT))

uart_modem = serial.Serial('/dev/tty.usbserial-146100', 9600, timeout = 0)
uart_modem.close()
uart_modem.open()
uart_modem.flushInput()
uart_modem.flushOutput()

startup( uart_modem )
socket = open_socket( uart_modem, 0, 1 )

def loop(delay):
	send_status_command( uart_modem, socket, 0, "0" )

	fluke_points = []

	idx = 0
	prev_do_fluke = 0

	start = time()
	cscon = 1
	while True:
		do_fluke = math.ceil( int( time() - start ) )
		if do_fluke % 5 is 0 and do_fluke is not prev_do_fluke:
			fluke_points.extend( handle_fluke_reading( sock ) )
			prev_do_fluke = do_fluke

		if int( time() - start ) > delay:
			break
	
	fluke_len = len( fluke_points )
	plt.plot( range( fluke_len ), fluke_points )
	avg_a = round( sum(fluke_points) / fluke_len, 6)
	# convert back to AMPERE
	plt.title( "POWER USAGE (avg: " + str( avg_a ) + "mA, " + str( avg_a * 3.3 ) + "mWh, " + str(fluke_len) + " samples)" )

	plt.show()
	sock.close()
	sys.exit()

if __name__ == "__main__":
	arguments = sys.argv[1:]
	print(sock)
	send_and_receive_fluke( sock, ":INIT")
	loop(int(arguments[0]))