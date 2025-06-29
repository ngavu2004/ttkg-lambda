# main_app/generate_share_link.py
import json
import boto3
import uuid
import os
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['GRAPH_CACHE_TABLE'])

def handler(event, context):
    try:
        body = json.loads(event['body'])
        file_id = body.get('file_id')
        graph_data = body.get('graph_data')  # The nodes and relationships
        
        if not file_id or not graph_data:
            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST, OPTIONS"
                },
                "body": json.dumps({"error": "Missing file_id or graph_data"})
            }
        
        # Generate unique share ID
        share_id = str(uuid.uuid4())
        
        # Set expiration (e.g., 30 days from now)
        expires_at = int((datetime.now() + timedelta(days=30)).timestamp())
        
        # Store in DynamoDB 
        # if a graph with the same file_id already exists, update it
        existing_item = table.get_item(Key={'file_id': file_id})
        if 'Item' in existing_item:
            # Update existing item
            table.update_item(
                Key={'file_id': file_id},
                UpdateExpression='SET graph_data = :data, expires_at = :expires, share_id = :share_id',
                ExpressionAttributeValues={
                    ':data': graph_data,
                    ':expires': expires_at,
                    ':share_id': share_id
                }
            )
        else:
            # Create new item
            table.put_item(
                Item={
                    'share_id': share_id,
                    'file_id': file_id,
                    'graph_data': graph_data,
                    'created_at': datetime.now().isoformat(),
                    'expires_at': expires_at,
                    'view_count': 0
                }
            )
        
        # Generate shareable URL
        # Build API Gateway URL dynamically from the event context
        api_id = event['requestContext']['apiId']
        region = event['requestContext']['accountId']  # Get from context
        stage = event['requestContext']['stage']
        
        # Alternative: Get region from environment
        region = os.environ.get('AWS_REGION', 'us-east-1')
        
        share_url = f"https://{api_id}.execute-api.{region}.amazonaws.com/{stage}/view-graph/{share_id}"
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST, OPTIONS"
            },
            "body": json.dumps({
                "share_id": share_id,
                "share_url": share_url,
                "expires_at": expires_at
            })
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"error": str(e)})
        }