# main_app/view_shared_graph.py
import json
import boto3
import os
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['GRAPH_CACHE_TABLE'])

def decimal_default(obj):
    """JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError

def handler(event, context):
    try:
        file_id = event['pathParameters']['file_id']
        
        # Query using the Global Secondary Index (FileIdIndex) instead of get_item
        response = table.query(
            IndexName='FileIdIndex',
            KeyConditionExpression='file_id = :file_id',
            ExpressionAttributeValues={':file_id': file_id}
        )

        if not response['Items']:
            return {
                "statusCode": 404,
                "headers": {
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps({"status": "Processing", "message": "Graph not found or being processed. Please try again in a few moments."})
            }

        item = response['Items'][0]
        
        # Convert the response data, handling Decimals
        response_data = {
            "status": "completed",
            "graph_data": item['graph_data'],
            "file_id": item['file_id'],
            "file_name": item.get('file_name', 'unknown'),
            "created_at": item['created_at'],
            "view_count": int(item.get('view_count', 0)) + 1  # Convert to int and add 1
        }
        
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "GET, OPTIONS"
            },
            "body": json.dumps(response_data, default=decimal_default)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"status": "error", "error": str(e)})
        }