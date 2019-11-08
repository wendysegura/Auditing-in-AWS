import boto3
import random


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
    return target

#print(generate_tennable_target_list(filter_ec2_instance(ec2_connect())))
generate_tennable_target_list(filter_ec2_instance(ec2_connect()))
