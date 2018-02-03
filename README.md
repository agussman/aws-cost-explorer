

Creating a python3 virtualenv:
```
$ which python3
/usr/local/bin/python3
$ mkvirtualenv --python=/usr/local/bin/python3 aws-cost-explorer
```

# AWS

## Create the Lambda function

Lambda > Functions > Create function
Name: monthlyBillingEmail
Runtime: Python 3.6
Role: Create a custom role

IAM Role: Create a new IAM Role
Role Name: lambda_send_billing_email

Create Function

## Creating IAM permissions

Create a Policy that allows access to the cost explorer API:

IAM > Policies > Create policy
Service: Cost Explorer Service
Actions: All
Name: allowCostExplorerRead

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": "ce:*",
            "Resource": "*"
        }
    ]
}
```



IAM > Policies > Create new 
Service: SES
Write: SendEmail, SendRawEmail
Name: allowSESSendEmail

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "VisualEditor0",
            "Effect": "Allow",
            "Action": [
                "ses:SendEmail",
                "ses:SendRawEmail"
            ],
            "Resource": "*"
        }
    ]
}
```

Bundle these Policies into a Role:

IAM > Roles > Search "lambda_send_billing_email"
Attach policy:
 - [x] allowCostExplorerRead
 - [x] allowSESSendEmail


## Actually create the Lambda function

Lambda > Functions > monthlyBillingEmail

We don't have any external libraries other than boto, so we can just edit inline

Paste the contents of `generate_report.py` into the `lambda_function` tab 
(except the shebang line although maybe that doesn't matter?)

Create a test, using Hello World as a template
(we're not actually using the contents so NBD)

Run the test; it should report success and the billing output

## Add Triggers

CloudWatch Events
Configure triggers
Create a new rule
  Rule name: lambda_monthly_billing
  Rule description: Running on the 3rd of the month
  Rule type: Schedule expression
  Schedule expression: `cron(0 0 3 * ? *)`  <- Syntax on this is a little wonky... need to have `?` for Day-of-month or Day-of-week


#References

* [AWS Cost Explorer API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/cost-explorer-api.html)
* [Boto 3 Docs on CostExplorer](http://boto3.readthedocs.io/en/latest/reference/services/ce.html)
* [Amazon SES Quick Start](https://docs.aws.amazon.com/ses/latest/DeveloperGuide/quick-start.html)
* [Boto 3 Docs on SES](http://boto3.readthedocs.io/en/latest/reference/services/ses.html)
* [Sample code creating attachments](https://gist.github.com/yosemitebandit/2883593)
* [AWS Schedule Expressions for Rules](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html)
