import json
import boto3
import os
import PyPDF2
import uuid
from datetime import datetime, timedelta

s3 = boto3.client('s3')
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')
BUCKET_NAME = os.environ['BUCKET_NAME']

def extract_text_from_pdf(file_path):
    text = ""
    with open(file_path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def generate_graph_json(text):
    try:
        # Get the actual function name from environment or construct it
        kg_function_name = os.environ.get('KG_FUNCTION_NAME', 'text-to-kg-KnowledgeGraphAPI-xyz')
        
        # Prepare the payload
        payload = {
            "body": json.dumps({"text": text})
        }
        
        # Invoke the knowledge graph function
        response = lambda_client.invoke(
            FunctionName=kg_function_name,
            InvocationType='RequestResponse',  # Synchronous
            Payload=json.dumps(payload)
        )
        
        # Parse the response
        result = json.loads(response['Payload'].read())
        
        if result.get('statusCode') == 200:
            return json.loads(result['body'])
        else:
            raise Exception(f"Knowledge graph function failed: {result}")
            
    except Exception as e:
        print(f"Error calling knowledge graph function: {str(e)}")
        raise e

def handler(event, context):
    try:
        for record in event['Records']:
            bucket = record['s3']['bucket']['name']
            key = record['s3']['object']['key']
            
            print(f"Processing S3 event - Bucket: {bucket}, Key: {key}")

            # Skip non-PDF files
            if not key.endswith('.pdf'):
                print(f"Skipping non-PDF file: {key}")
                continue

            # Parse the key to extract file_id and file_name
            # Expected format: uploads/{file_id}/{original_filename}
            key_parts = key.split('/')
            if len(key_parts) < 3:
                print(f"Invalid key format: {key}. Expected: uploads/file_id/filename")
                continue
                
            file_id = key_parts[1]
            file_name = key_parts[-1]  # Get the original filename
            
            # Create a unique download path using file_id to avoid conflicts
            download_path = f"/tmp/{file_id}_{file_name}"
            
            print(f"Extracted - File ID: {file_id}, File Name: {file_name}")
            print(f"Download path: {download_path}")

            try:
                # Check if the object exists before downloading
                s3.head_object(Bucket=bucket, Key=key)
                print(f"Object confirmed to exist: s3://{bucket}/{key}")
                
                # Download the file
                s3.download_file(bucket, key, download_path)
                print(f"Successfully downloaded file to: {download_path}")
                
            except s3.exceptions.NoSuchKey:
                print(f"ERROR: S3 object not found: s3://{bucket}/{key}")
                continue
            except Exception as download_error:
                print(f"ERROR: Failed to download file: {str(download_error)}")
                continue

            try:
                # Extract text from PDF
                extracted_text = extract_text_from_pdf(download_path)
                print(f"Extracted text length: {len(extracted_text)} characters")
                print(f"Text preview: {extracted_text[:200]}...")

                # Generate knowledge graph
                graph_json = generate_graph_json(extracted_text)
                print(f"Generated knowledge graph with {len(graph_json.get('nodes', []))} nodes and {len(graph_json.get('edges', []))} edges")
                
            except Exception as processing_error:
                print(f"ERROR: Failed to process file content: {str(processing_error)}")
                # Store error in DynamoDB for polling endpoint
                table = dynamodb.Table(os.environ['GRAPH_CACHE_TABLE'])
                table.put_item(
                    Item={
                        'share_id': str(uuid.uuid4()),
                        'file_id': file_id,
                        'file_name': file_name,
                        'status': 'error',
                        'error_message': str(processing_error),
                        'created_at': datetime.now().isoformat(),
                        'expires_at': int((datetime.now() + timedelta(days=7)).timestamp()),  # Shorter expiration for errors
                        'view_count': 0
                    }
                )
                continue

            try:
                # Save successful result to DynamoDB
                table = dynamodb.Table(os.environ['GRAPH_CACHE_TABLE'])
                table.put_item(
                    Item={
                        'share_id': str(uuid.uuid4()),  # Generate a unique share ID
                        'file_id': file_id,
                        'file_name': file_name,
                        'graph_data': graph_json,
                        'status': 'completed',
                        'created_at': datetime.now().isoformat(),
                        'expires_at': int((datetime.now() + timedelta(days=30)).timestamp()),  # 30 days expiration
                        'view_count': 0
                    }
                )
                print(f"Successfully saved graph data to DynamoDB for file_id: {file_id}")
                
            except Exception as db_error:
                print(f"ERROR: Failed to save to DynamoDB: {str(db_error)}")
                continue
            
            finally:
                # Clean up temporary file
                try:
                    if os.path.exists(download_path):
                        os.remove(download_path)
                        print(f"Cleaned up temporary file: {download_path}")
                except Exception as cleanup_error:
                    print(f"Warning: Failed to clean up temporary file: {str(cleanup_error)}")

        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Processing completed'})
        }
        
    except Exception as e:
        print(f"ERROR: Unexpected error in handler: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }