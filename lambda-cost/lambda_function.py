import boto3
import json
from datetime import date, timedelta
from decimal import Decimal
import random

# DynamoDB table
dynamodb = boto3.resource('dynamodb', region_name='us-east-2')  # set your region
table = dynamodb.Table('AWS_Cost_Usage')

# List of common AWS services
services = [
    'AWS Lambda',
    'Amazon API Gateway',
    'Amazon DynamoDB',
    'Amazon S3',
    'Amazon EC2',
    'Amazon CloudWatch',
    'AWS Step Functions',
    'Amazon SNS'
]

def generate_dummy_data(days=14):
    """Generate realistic dummy data for the past `days` days."""
    dummy_data = []
    today = date.today()
    for i in range(days):
        day = today - timedelta(days=i)
        date_str = day.isoformat()
        for service in services:
            cost = Decimal(f"{random.uniform(0.10, 5.00):.2f}")
            dummy_data.append({
                'date': date_str,
                'service': service,
                'cost': cost
            })
    return dummy_data

def lambda_handler(event, context):
    client = boto3.client('ce')  # Cost Explorer client

    end = date.today()
    start = end - timedelta(days=1)  # Yesterday only

    try:
        # Fetch real AWS cost data
        response = client.get_cost_and_usage(
            TimePeriod={
                'Start': start.isoformat(),
                'End': end.isoformat()
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}]
        )

        results_found = False
        real_data_items = []

        # Prepare real AWS cost data for insertion
        for day in response['ResultsByTime']:
            date_str = day['TimePeriod']['Start']
            for group in day['Groups']:
                service = group['Keys'][0]
                cost = Decimal(group['Metrics']['UnblendedCost']['Amount'])
                if cost > 0:
                    results_found = True
                    real_data_items.append({
                        'date': date_str,
                        'service': service,
                        'cost': cost
                    })

        # Insert real AWS data if found
        if results_found:
            with table.batch_writer() as batch:
                for item in real_data_items:
                    batch.put_item(Item=item)
            return {
                'statusCode': 200,
                'body': json.dumps({'message': f'{len(real_data_items)} real AWS items inserted'})
            }

        # Otherwise insert 2 weeks of dummy data
        dummy_data = generate_dummy_data(days=14)
        with table.batch_writer() as batch:
            for item in dummy_data:
                batch.put_item(Item=item)

        return {
            'statusCode': 200,
            'body': json.dumps({'message': f'{len(dummy_data)} dummy items inserted'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
