from pymongo import MongoClient
import argparse
import numpy as np

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description='NB IoT LABTEST.')

	parser.add_argument('--h', help='help')
	parser.add_argument('-c', action='store', dest='collection', help='Set collection', type=str, default='')
	parser.add_argument('-start', action='store', dest='start_date', help='Set start date', type=str, default='')
	parser.add_argument('-end', action='store', dest='end_date', help='Set end date', type=str, default='')


	# Parse arguments from user
	r = parser.parse_args()

	client = MongoClient("localhost", 27017, maxPoolSize=50)
	db = client['sensordb']
	collection = db[r.collection]
	cursor = None
	if r.start_date == '':
		cursor = collection.find({})
	else:
		cursor = collection.find({
			"timestamp": {
		        "$gte": r.start_date,
		        "$lt": r.end_date
	    	}
		})

	uptime = []
	counter = 0
	temp = 0
	previous_msg_id = 0
	ignore_result = False
	for document in cursor:
		msg_id = int(document['msg_id'])
		if msg_id == 1 and previous_msg_id > 20:
			calc = (counter / previous_msg_id) * 100
			uptime.append( [previous_msg_id, counter, calc ] )
			counter = 0
			temp = 0

		previous_msg_id = msg_id
		counter += 1

	if previous_msg_id != 0:
		calc = (counter / previous_msg_id) * 100
		uptime.append( [previous_msg_id, counter, calc ] )

	print( 'Statistics about collection: ', r.collection)
	for elem in uptime:
		print ('Transmits: ', elem[0])
		print ('Received transmits: ', elem[1])
		print ('Uptime: ', elem[2])

	print( 'Total uptime: ', np.mean(uptime, axis=0))

