from time import *
import datetime
import string
import random

def send_and_receive_fluke( sock, command ):
    packet = (command + "\n").encode('utf-8')
    sock.send(packet)

    if ":INIT" not in command or "FETCH" in command:
    	reply = sock.recv(300000).decode('utf-8')
    	return reply

def remove_high_convert_to_ma(x):
	return x * 1000 if x < 1000 else None

def remove_high_coverage(x):
	return x if (x > -120 and x < 0) else None

def create_2d(x):
	return [datetime.datetime.utcnow()][x]

def remove_bad_data( the_list, lower_limit, upper_limit):
	new_list = []
	for elem in the_list:
		if elem >= lower_limit and elem <= upper_limit:
			new_list.append(elem)
	return new_list

def filter_undefined( x ):
	if x is not None and len(x) < 20:
		return x

def handle_fluke_reading( sock ):
	buffer = send_and_receive_fluke( sock, ":FETCH?; :INIT").replace("\r\n","").split(',')
	buffer = list( filter(filter_undefined, buffer) )
	numbers = map( float, buffer )
	return numbers

def read_once( modem ):
	try:
		return modem.read(300).decode('utf-8')
	except Exception as e:
		print (e)
		return "ERROR"

def read( modem, delimiter ):
	try:
		read = modem.read(300).decode('utf-8')
		counter = 0

		while counter < 500000 and delimiter not in read:
			read += modem.read(300).decode('utf-8')
			if "ERROR" in read:
				return "ERROR"

			counter += 1
		
		return read
	except Exception as e:
		print (e)
		return "ERROR"

	
def write( modem, command ):
	old_buffer = read_once( modem )
	if len( old_buffer ) is not 0:
		print( old_buffer )

	try:
		return modem.write( command.encode('utf-8') )
	except Exception as e:
		print (e)
		raise -1

def startup_command( modem, command ):
	read_once( modem )

	write( modem, command + "\r\n" )
	if read( modem, "OK" ) is "ERROR":
		print( command, " - ERROR" )

def reboot( modem ):
	read_once( modem )
	write( modem, "AT+NRB" + "\r\n" )

def startup( modem ):
	startup_command( modem, "AT+CEREG=5" )
	startup_command( modem, "AT+CSCON=1" )
	startup_command( modem, "AT+NPSMR=1" )
	
#AT+NSOCR="DGRAM",17,1,1
def open_socket( modem, socket, start_port ):
	if socket:
		write( modem, "AT+NSOCL=" + str(socket) )

	port = start_port
	open_socket = "ERROR"

	while "RESET" in open_socket or "ERROR" in open_socket or len(open_socket.split("\n")) == 1:
		write( modem, "AT+NSOCR=\"DGRAM\",17," + str(port) + ",1\r\n" )
		open_socket = read(modem, "OK")
		port += 1

	socket = open_socket.split('\n')[1][:-1]
	print( "Using socket: ", socket)
	return socket

def close_socket( modem, socket ):
	write( modem, "AT+NSOCL=" + str(socket) )

def find_index_with_delimiter( delimiter, l ):
	for i, elem in enumerate( l ):
		if delimiter in elem:
			return i;

	return -1

def get_nuestats( modem ):
	write( modem, "AT+NUESTATS\r\n" )

	nuestats = read( modem, "OK" )

	splitted = nuestats.split('\n')

	ok_index = find_index_with_delimiter( "OK", splitted )
	if "ERROR" not in nuestats or ok_index != -1 or ok_index < 10 and "Signal power" in splitted[0]:
		nuestats_list = []
		nuestats_list.append( splitted[ok_index - 12].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 11].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 10].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 9].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 8].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 7].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 6].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 5].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 4].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 3].split(',')[-1][:-1] )
		nuestats_list.append( splitted[ok_index - 2].split(',')[-1][:-1] )

		return nuestats_list
	else:
		return "ERROR"

def sendToXBytes( modem, bytes, socket, id, release_indicator):
	data_string = ''.join(random.choice(string.ascii_uppercase) for x in range(bytes))

	payload = ""
	for c in data_string:
		payload += hex(ord(c)).upper()[2:]

	length = int( (len(payload) / 2) )

	flag = "0x0"
	if release_indicator is 1:
		flag = "0x200"
	command = "AT+NSOSTF=" + str(socket) + ",\"158.39.77.97\",5683," + flag + "," + str(length) + ",\"" + payload + "\""
	print( command )
	write( modem, command + "\r\n" )
	print ( "rsp: " + read( modem, "OK" ) )

def sendTo( modem, data, socket, id, release_indicator):
	payload = "5002" + "30" + "30B1" + hex(ord(id)).upper()[2:] + "112AFF" + data

	flag = "0x0"
	if release_indicator == 1:
		flag = "0x200"

	length = int( (len(payload) / 2) )
	command = "AT+NSOSTF=" + str(socket) + ",\"158.39.77.97\",5683," + flag + "," + str(length) + ",\"" + payload + "\""
	print( command )
	write( modem, command + "\r\n" )
	print ( "rsp: " + read( modem, "OK" ) )

def send_status_command( modem, socket, msg_id, id, release_indicator ):
	write( modem, "AT+CSCON=1\r\n" )

	read( modem, "OK" )

	nuestats_list = get_nuestats( modem )
			
	if nuestats_list is not "ERROR":
		utcnow = datetime.datetime.utcnow()
		nuestats_list.append( utcnow.isoformat() )
		nuestats_list.append( str(msg_id) )

		print( nuestats_list )

		data = ""
		for elem in nuestats_list:
			hex_elem = ""
			for c in elem:
				hex_elem += hex(ord(c)).upper()[2:]
			data += hex_elem + hex(ord('_')).upper()[2:]

		sendTo( modem, data, socket, id, release_indicator)		

def get_cereg( modem ):
	read_once( modem )

	write( modem, "AT+CEREG?\r\n" )

	nuestats = read( modem, "OK" )

	splitted = nuestats.split('\n')
	cereg_index = find_index_with_delimiter( "+CEREG", splitted )
	cereg = splitted[cereg_index].split(':')[-1].split(',')[1]

	if len(cereg) > 0:
		try:
			return int(cereg)
		except Exception as e:
			print (e)

def get_cscon( modem ):
	read_once( modem )

	write( modem, "AT+CSCON?\r\n" )

	nuestats = read( modem, "OK" )

	splitted = nuestats.split('\n')
	cscon_index = find_index_with_delimiter( "+CSCON", splitted )
	cscon = splitted[cscon_index].split(':')[-1].split(',')[-1][:-1]

	if len(cscon) > 0:
		try:
			return int(cscon)
		except Exception as e:
			print (e)

def get_npsmr( modem ):
	read_once( modem )

	write( modem, "AT+NPSMR?\r\n" )

	nuestats = read( modem, "OK" )

	splitted = nuestats.split('\n')
	npsmr_index = find_index_with_delimiter( "+NPSMR", splitted )
	npsmr = splitted[npsmr_index].split(':')[-1].split(',')[-1][:-1]

	if len(npsmr) > 0:
		try:
			return int(npsmr)
		except Exception as e:
			print (e)

def wait_for_psm( modem ):
	while True:
		psm = get_npsmr( modem )
		print(psm)
		if psm is 1:
			return
		else:
			sleep(1)

def check_negative(v):
    """
    Check if user inputs negative value or string to an int variable
    :param v: User input
    :return:
    """
    try:
        value = int(v)
        if value < 0:
            raise TypeError
        else:
            return True
    except Exception:
        raise TypeError

