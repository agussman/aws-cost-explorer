#!/usr/bin/env python3

import boto3
import datetime
import re

from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart

from botocore.exceptions import ClientError


def lambda_handler(event, context):
    # Create a Cost Explorer client
    client = boto3.client('ce')

    # Set time range to cover the last full calendar month
    # Note that the end date is EXCLUSIVE (e.g., not counted)
    now = datetime.datetime.utcnow()
    # Set the end of the range to start of the current month
    end = datetime.datetime(year=now.year, month=now.month, day=1)
    # Subtract a day and then "truncate" to the start of previous month
    start = end - datetime.timedelta(days=1)
    start = datetime.datetime(year=start.year, month=start.month, day=1)
    # Get the month as string for email purposes
    month = start.strftime('%Y-%m')

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

    tsv_lines = []
    for project in response["ResultsByTime"][0]["Groups"]:
        namestring = project['Keys'][0]
        name = re.search("\$(.*)", namestring).group(1)
        if name is None or name == "":
            name = "Other"

        amount = project['Metrics']['BlendedCost']['Amount']
        amount = float(amount)
        line = "{}\t${:,.2f}".format(name, amount)
        print(line)
        tsv_lines.append(line)


    send_email(month, "\n".join(tsv_lines))




def send_email(month, attachment):
    msg = MIMEMultipart()
    msg['From']  = "Aaron Gussman <aaron.gussman@digitalglobe.com>"
    msg['To'] = "aaron.gussman@digitalglobe.com"
    msg['Subject'] = "Monthly AWS Cost Breakdown: {}".format(month)

    # what a recipient sees if they don't use an email reader
    msg.preamble = 'Multipart message.\n'

    # the message body
    part = MIMEText('Here is the aws billing data from last month.')
    msg.attach(part)

    # the attachment
    part = MIMEApplication(attachment)
    part.add_header('Content-Disposition', 'attachment', filename="AWS-MonthlyCostByProject-{}.tsv".format(month))
    msg.attach(part)

    # Create an AWS Simple Email Service (SES) client
    client = boto3.client('ses')

    try:
        response = client.send_raw_email(
            RawMessage={
                 'Data': msg.as_string(),
            },
            #Source=msg['From'],
            #Destinations=to_emails
        )
    # Display an error if something goes wrong.
    except ClientError as e:
        print(e.response['Error']['Message'])
    else:
        print("Email sent! Message ID:"),
        print(response['ResponseMetadata']['RequestId'])



if __name__ == "__main__":
    lambda_handler({}, {})
