import boto3
import random
import datetime


import argparse
import os
from datetime import datetime
from tenable_io.api.models import Scan
from tenable_io.api.scans import ScanExportRequest
from tenable_io.client import TenableIOClient
from tenable_io.exceptions import TenableIOApiException
from tenable_io.exceptions import TenableIOException
from time import time

from botocore.exceptions import ClientError
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

parser = argparse.ArgumentParser(description='configuration of nessus tenable account')
parser.add_argument('-a', '--tenable_key', required=True, help='access key')
parser.add_argument('-k', '--tenable_secret', required=True, help='secret key')

args = parser.parse_args()
tenable_key = args.tenable_key
tenable_secret = args.tenable_secret

# Connect to EC2
def ec2_connect():
    ec2 = boto3.resource('ec2')
    instances = ec2.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}])
    return instances

def filter_ec2_instance(ec2_connect):
    for i in ec2_connect:
        for tag in i.tags:
            if 'role'in tag['Key']:
                i.Name = tag['Value']
    public_ips = [each_instance.public_ip_address for each_instance in ec2_connect]
    return random.sample((public_ips), 5)


def generate_tennable_target_list(filter_ec2_instance):
    target = []
    target = ','.join(filter_ec2_instance)
    print(target)
    return target

def tenable_client():
	return TenableIOClient(tenable_key, tenable_secret)

def create_scan(tenable_client):
	import time
	timestr = time.strftime("%Y%m%d-%H%M%S")
	scan_name = u"scanjob_" + timestr
	scan = tenable_client().scan_helper.create(name=scan_name, text_targets='generate_tennable_target_list', template='basic')
	return scan

def launch_scan(create_scan):
	create_scan.launch().download('/Path/to/scan_name.pdf')
	first_scan_id = min([int(history.history_id) for history in create_scan.histories()])
	assert os.path.isfile('/Path/to/scan_name.pdf')
	return('/Path/to/scan_name.pdf')

	# check that path does exist script won't work without this bit not sure why
	path = ['/Users/wsegura/Desktop/scan_name.pdf']
	f = 'Users'
	for p in path:
		f = os.path.joint(f, p)
		print(f)
		assert os.path.exists(f)
	assert os.path.isfile(f)

def email_subject(sender, recipient):
	#https://docs.aws.amazon.com/ses/latest/DeveloperGuide/examples-send-using-sdk.html
    SENDER = "sender@email.com"
    RECIPIENT = "recipient@email.com"
    AWS_REGION = "us-west-2"
    SUBJECT = "Weekly Nessus Scan Report"
    ATTACHMENT = "/Path/to/scan_name.pdf"
    BODY_TEXT = "Hello,\r\nPlease see the attached weekly nessus scan report."
    BODY_HTML = """\
	<html>
	<head></head>
	<body>
	<h2>Hello!</h2>
	<p>Please see the attached weekly nessus scan report..</p>
	</body>
	</html>
	"""
    CHARSET = "utf-8"
    
    client = boto3.client('ses',region_name=AWS_REGION)
    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT  
    msg['From'] = SENDER 
    msg['To'] = RECIPIENT
    msg_body = MIMEMultipart('alternative')

    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)
    att = MIMEApplication(open(ATTACHMENT, 'rb').read())
    att.add_header('Content-Disposition','attachment',filename=os.path.basename(ATTACHMENT))
    msg.attach(msg_body)
    msg.attach(att)
    try:
	    response = client.send_raw_email(
	        Source=SENDER,
	        Destinations=[
	            RECIPIENT
	        ],
	        RawMessage={
	            'Data':msg.as_string(),
	        }
	    )	
    except ClientError as e:
	    print(e.response['Error']['Message'])
    else:
	    print("Email sent! Message ID:"),
	    print(response['MessageId'])

def main():
    generate_tennable_target_list(filter_ec2_instance(ec2_connect()))
    launch_scan(create_scan(tenable_client))
    email_subject('sender', 'recipient')
    
if __name__ == '__main__':
  main()
