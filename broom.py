import csv
import boto3
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--region', '-r', help='AWS region name', required=True)
parser.add_argument('--profile', '-p', help='Local AWS profile for key and secret', required=False)
args = parser.parse_args()

session = boto3.Session(profile_name=args.profile)
client = session.client('ec2', region_name=args.region)

all_groups = []
security_groups_in_use = []

# Get ALL security groups names
security_groups_dict = client.describe_security_groups()
security_groups = security_groups_dict['SecurityGroups']
for groupobj in security_groups:
    all_groups.append(groupobj['GroupId'])

network_interfaces_dict = client.describe_network_interfaces()
network_interfaces = network_interfaces_dict['NetworkInterfaces']

for networkobj in network_interfaces:
    for group in networkobj['Groups']:
        security_groups_in_use.append(group['GroupId'])

diff = list(set(all_groups) - set(security_groups_in_use))

sg_list = client.describe_security_groups(GroupIds=diff)

dump = [['Group name', 'Group id', 'Description', 'VPC id', 'Tags', 'Ingress', 'Egrass']]

for sg in sg_list['SecurityGroups']:
    row = []
    row.append(sg['GroupName'])
    row.append(sg['GroupId'])
    row.append(sg['Description'])
    row.append(sg['VpcId'])
    try:
        row.append(sg['Tags'])
    except:
        pass
    row.append(sg['IpPermissions'])
    row.append(sg['IpPermissionsEgress'])
    dump.append(row)

with open('securitygroups.csv', 'w') as csvFile:
    writer = csv.writer(csvFile)
    writer.writerows(dump)

csvFile.close()

