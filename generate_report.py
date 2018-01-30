#!/usr/bin/env python3

import boto3
import datetime
import pprint

client = boto3.client('ce')

now = datetime.datetime.utcnow()
start = (now - datetime.timedelta(days=2)).strftime('%Y-%m-%d')
end = now.strftime('%Y-%m-%d')


response = client.get_cost_and_usage(
    TimePeriod={
        'Start': start,
        'End':  end
    },
    Granularity='DAILY',
    Metrics=['BlendedCost'],
    GroupBy=[
        {
            'Type': 'TAG',
            'Key': 'Project'
        },
    ]
)

pprint.pprint(response)
