import argparse
import os
from datetime import datetime
from tenable_io.api.models import Scan
from tenable_io.api.scans import ScanExportRequest
from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException
from tenable_io.exceptions import TenableIOException
from time import time


parser = argparse.ArgumentParser(description='configuration of nessus tenable account')
parser.add_argument('-a', '--tenable_key', required=True, help='access key')
parser.add_argument('-k', '--tenable_secret', required=True, help='secret key')

args = parser.parse_args()
tenable_key = args.tenable_key
tenable_secret = args.tenable_secret

def tenable_client():
	return TenableIOClient(tenable_key, tenable_secret)

def create_scan(tenable_client):
	import time
	timestr = time.strftime("%Y%m%d-%H%M%S")
	scan_name = u"scanjob_" + timestr
	scan = tenable_client().scan_helper.create(name=scan_name, text_targets='[input ip_address]', template='basic')
	return scan

def launch_scan(create_scan):
	create_scan.launch().download('path/to/download/scan_name.pdf')
	first_scan_id = min([int(history.history_id) for history in create_scan.histories()])
	assert os.path.isfile('/path/to/scan_name.pdf')
	return('~/scan_name.pdf')

	# check that path does exist script won't work without this bit not sure why
	path = ['~/scan_name.pdf']
	f = 'Users'
	for p in path:
		f = os.path.joint(f, p)
		print(f)
		assert os.path.exists(f)
	assert os.path.isfile(f)

launch_scan(create_scan(tenable_client))

#https://github.com/tenable/Tenable.io-SDK-for-Python/tree/8a78ae3e03f17dbf803cebd476e63d5a725ac5c4
#https://tenableio-python-sdk.readthedocs.io/en/latest/tenable_io.api.html

