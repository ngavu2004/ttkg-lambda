# upload_file.py
import json
import boto3
import base64
import uuid
import os
from datetime import datetime
import PyPDF2
from io import BytesIO
import docx

s3_client = boto3.client('s3')
BUCKET_NAME = os.environ['BUCKET_NAME']

def extract_text_from_file(file_content, content_type, file_name):
    """Extract text during upload"""
    try:
        if content_type.startswith('text/') or file_name.endswith('.txt'):
            return file_content.decode('utf-8')
        
        elif file_name.endswith('.pdf'):
            pdf_file = BytesIO(file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        
        elif file_name.endswith('.docx'):
            doc_file = BytesIO(file_content)
            doc = docx.Document(doc_file)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            return text.strip()
        
        else:
            # Try as text
            return file_content.decode('utf-8')
            
    except Exception as e:
        raise Exception(f"Failed to extract text: {str(e)}")

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        file_content = body.get('file_content')
        file_name = body.get('file_name', 'uploaded_file.txt')
        content_type = body.get('content_type', 'text/plain')
        
        if not file_content:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No file content provided"})
            }
        
        # Decode file
        file_data = base64.b64decode(file_content)
        file_id = str(uuid.uuid4())
        
        # Extract text immediately
        try:
            extracted_text = extract_text_from_file(file_data, content_type, file_name)
            if not extracted_text.strip():
                return {
                    "statusCode": 400,
                    "body": json.dumps({"error": "No text could be extracted from file"})
                }
        except Exception as e:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": str(e)})
            }
        
        # Store original file
        original_key = f"uploads/{file_id}/original/{file_name}"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=original_key,
            Body=file_data,
            ContentType=content_type,
            Metadata={
                'file_id': file_id,
                'original_filename': file_name,
                'upload_timestamp': datetime.utcnow().isoformat()
            }
        )
        
        # Store extracted text
        text_key = f"uploads/{file_id}/extracted.txt"
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=text_key,
            Body=extracted_text.encode('utf-8'),
            ContentType='text/plain',
            Metadata={
                'file_id': file_id,
                'original_filename': file_name,
                'text_length': str(len(extracted_text)),
                'extraction_timestamp': datetime.utcnow().isoformat()
            }
        )
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "file_id": file_id,
                "original_filename": file_name,
                "text_length": len(extracted_text),
                "message": "File uploaded and text extracted successfully",
                "process_url": f"/process_file/{file_id}"
            })
        }
        
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }