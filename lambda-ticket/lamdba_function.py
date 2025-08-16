import json
import boto3
import uuid
from datetime import datetime

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('SupportTickets')  # Table name must match DynamoDB table

def lambda_handler(event, context):
    print("Received event:", event)  # For debugging

    # Parse message from event body
    message_body = json.loads(event.get('body', '{}'))
    message = message_body.get('message', 'No message provided')

    # Generate ticket ID and timestamp
    ticket_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()

    # Store in DynamoDB
    table.put_item(
        Item={
            'ticket_id': ticket_id,
            'message': message,
            'timestamp': timestamp
        }
    )

    # Response
    return {
        'statusCode': 200,
        'body': json.dumps({
            'ticket_id': ticket_id,
            'message': message
        })
    }
