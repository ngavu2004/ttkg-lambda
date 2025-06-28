import os
import boto3
import json
import uuid
from datetime import datetime, timedelta

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

def handler(event, context):
    query_params = event.get('queryStringParameters') or {}
    file_name = query_params.get('file_name', f'file-{uuid.uuid4()}.txt')
    content_type = query_params.get('content_type', 'application/octet-stream')
    file_id = str(uuid.uuid4())

    # Generate a presigned URL for uploading
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET_NAME, 
                'Key': f"uploads/{file_id}/{file_name}",
                'ContentType': content_type
            },
            ExpiresIn=3600
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "presigned_url": presigned_url,
                "file_name": file_name,
                "file_id": file_id,
            })
        }
    except Exception as e:
        print(f"Error: {e}")
        return {
            "statusCode": 500,
            "body": {"error": str(e)}
        }