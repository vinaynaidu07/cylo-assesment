import boto3

client = boto3.client('ec2')

paginator = client.get_paginator('describe_instances')


def handler():
    special_ec2_id = get_tagged_instance_ids()
    total_ec2_id = get_all_instances_ids()
    raw_ec2_ids = [ item for item in total_ec2_id if item not in special_ec2_id] #check only instances without special tag
    raw_sggrp_ids = get_all_sg_ids(raw_ec2_ids)
    get_and_delete_rules(raw_sggrp_ids)


def get_tagged_instance_ids():
    special_ec2_id = []
    response_iterator = paginator.paginate(
        Filters=[
            {
                'Name': 'tag:<key>',
                'Values': [
                    '<value>',
                ]
            },
        ]
    )
    for each in response_iterator['Reservations']:
        for item in each['Instances']:
            special_ec2_id.append(item['InstanceId'])
    return special_ec2_id
def get_all_instances_ids():
    total_ec2_id = []
    total_response_iterator = paginator.paginate()
    for each in total_response_iterator['Reservations']:
        for item in each['Instances']:
            total_ec2_id.append(item['InstanceId'])
    return total_ec2_id






def get_all_sg_ids(raw_ec2_ids):
    
    for each in raw_ec2_ids:
        sg_response_iterator = paginator.paginate(
            Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [
                        each
                    ]
                },
            ]
        )
        for each in sg_response_iterator['Reservations']:
            for item in each['Instances']:
                for sggrp in item['SecurityGroups']:
                    raw_sggrp_ids.append('GroupId')
    return raw_sggrp_ids

def get_and_delete_rules(raw_sggrp_ids):
    response = client.describe_security_groups(
        Filters=[
            {
                'Name': 'ip-permission.cidr',
                'Values': [
                    '0.0.0.0/0',
                ]
            },
            {
                'Name': 'ip-permission.from-port',
                'Values': ['22']
            }
        ],
        GroupIds=[
            id for id in raw_sggrp_ids
        ]
    )
    for sg in response['SecurityGroups']:
        actual_sggrp_ids.append(sg['GroupId'])

    for each in actual_sggrp_ids:
        ec2 = boto3.resource('ec2')
        security_group = ec2.SecurityGroup(each)
        response = security_group.revoke_ingress(
            CidrIp='0.0.0.0/0',
            FromPort=22,
            IpPermissions=[
                {
                    'FromPort': 22,
                    'IpProtocol': 'tcp',
                    'IpRanges': [
                        {
                            'CidrIp': '0.0.0.0/0',
                        },
                    ],
                    'ToPort': 22,
                },
            ],
            IpProtocol='tcp',
            ToPort=22,
        )

if __name__ == "__main__":
    handler()