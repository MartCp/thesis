import csv
import json
import argparse
import datetime

parser = argparse.ArgumentParser(description="Import records into MongoDB")  
parser.add_argument("path", help="The input path for importing. This can be either a file or directory.")  
args = parser.parse_args()

csvfile = open(args.path, 'r')
jsonfile = open(args.path + '.json', 'w')

fieldnames = ("site_id","sensor_id","uid","idx","http_date","log_date","http_client_ip_address","message_type","occupancy","battery_voltage","battery_status","temperature","rssi","reset_cause","reset_counter","channel","ch_rssi","nonce","image_before","image_after","raw_mag_x","raw_mag_y","raw_mag_z","raw_radar_fp","raw_radar_tx_lev_fp","raw_radar_peak","raw_radar_total","raw_mag_diff","raw_mag_diff_type","long_version","long_pa_power","long_radar_count","long_radar_blocked","long_reserved","cell_sig_pwr","cell_tot_pwr","cell_tx_pwr","cell_rx_time","cell_tx_time","cell_cellid","cell_ecl","cell_snr","cell_earfcn","cell_pci","cell_rsrq","cell_drx3","cell_psm4","cell_psm5","cell_ublox_boot_counter","cell_ublox_analog_active_ticks","cell_send_counter","cell_recv_counter","info_ue_hardware","info_ue_firmware","info_ue_imei","info_sim_imsi","info_sim_cid")
reader = csv.DictReader( csvfile, fieldnames)

for row in reader:
	data = {}

	cell_recv_counter = row['cell_recv_counter']

	http_date = datetime.datetime.strptime(row['http_date'], "%Y-%m-%d %H:%M:%S.%f")

	latency = 0

	if cell_recv_counter != 'NULL':
		http_date_int = (http_date-datetime.datetime(1970,1,1)).total_seconds() * 1000
		latency = ((http_date_int % (1000 * 3600)) - float(cell_recv_counter)) / 1000
		if latency < 0:
			latency += (1000 * 3600)

	data['timestamp'] = row['http_date']
	data['latency'] = latency
	data['msg_id'] = row['idx']
	data['ip'] = row['http_client_ip_address']

	data['signal_power'] = row['cell_sig_pwr']
	data['tx_power'] = row['cell_tx_pwr']
	data['tx_time'] = row['cell_tx_time']
	data['rx_time'] = row['cell_rx_time']
	data['cell_id'] = row['cell_cellid']
	data['ecl'] = row['cell_ecl']
	data['earfcn'] = row['cell_earfcn']
	data['pci'] = row['cell_pci']
	data['rsrq'] = row['cell_rsrq']

	json.dump(data, jsonfile)
	jsonfile.write('\n')