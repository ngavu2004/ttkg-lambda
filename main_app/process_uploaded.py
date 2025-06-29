import json
import boto3
import os
import PyPDF2
import uuid

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
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        if not key.endswith('.pdf'):
            continue

        file_id = key.split('/')[1]
        download_path = f"/tmp/{file_id}.pdf"
        output_key = f"uploads/{file_id}/knowledge_graph.json"

        print(f"Processing file: {key} from bucket: {bucket}")

        # Download the file
        s3.download_file(bucket, key, download_path)
        print(f"Downloaded file to: {download_path}")

        extracted_text = extract_text_from_pdf(download_path)
        print(f"Extracted text from PDF: {extracted_text[:100]}...")

        graph_json = generate_graph_json(extracted_text)
        print(f"Generated knowledge graph JSON: {graph_json}")
        
        # Convert the dictionary to JSON string before uploading
        graph_json_string = json.dumps(graph_json, indent=2)

        # save json to dynamodb
        table = dynamodb.Table(os.environ['GRAPH_CACHE_TABLE'])

        table.put_item(
            Item={
                'file_id': file_id,
                'graph_data': graph_json,
                'created_at': int(context.timestamp),
                'expires_at': int((context.timestamp + 30 * 24 * 60 * 60)),  # 30 days expiration
                'view_count': 0
            }
        )

    return {
        'statusCode': 200,
        'body': graph_json_string
    }