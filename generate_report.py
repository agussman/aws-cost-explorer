#!/usr/bin/env python3

import boto3
import datetime
import pprint
import re

from botocore.exceptions import ClientError


def lambda_handler(event, context):
    client = boto3.client('ce')

    # Set time range to cover the last full calendar month
    # Note that the end date is EXCLUSIVE (e.g., not counted)
    now = datetime.datetime.utcnow()
    # Set the end of the range to start of the current month
    end = datetime.datetime(year=now.year, month=now.month, day=1)
    # Subtract a day and then "truncate" to the start of previous month
    start = end - datetime.timedelta(days=1)
    start = datetime.datetime(year=start.year, month=start.month, day=1)
    # Convert them to strings
    start = start.strftime('%Y-%m-%d')
    end = end.strftime('%Y-%m-%d')


    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start,
            'End':  end
        },
        Granularity='MONTHLY',
        Metrics=['BlendedCost'],
        GroupBy=[
            {
                'Type': 'TAG',
                'Key': 'Project'
            },
        ]
    )

    #pprint.pprint()

    for project in response["ResultsByTime"][0]["Groups"]:
        namestring = project['Keys'][0]
        name = re.search("\$(.*)", namestring).group(1)
        if name is None or name == "":
            name = "Other"

        amount = project['Metrics']['BlendedCost']['Amount']
        amount = float(amount)
        print("{}\t${:,.2f}".format(name, amount))


    send_email("Holla!")



#TODO: attachment: https://gist.github.com/yosemitebandit/2883593
def send_email(body):
    SENDER = "Aaron Gussman <aaron.gussman@digitalglobe.com>"
    RECIPIENT = "aaron.gussman@digitalglobe.com"
    SUBJECT = "Amazon SES Test (SDK for Python)"

    client = boto3.client('ses')

    try:
        #Provide the contents of the email.
        response = client.send_email(
            Destination={
                'ToAddresses': [
                    RECIPIENT,
                ],
            },
            Message={
                'Body': {
                    'Text': {
                        'Data': body,
                    },
                },
                'Subject': {
                    'Data': SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            #ConfigurationSetName=CONFIGURATION_SET,
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['ResponseMetadata']['RequestId'])



if __name__ == "__main__":
    lambda_handler({}, {})
