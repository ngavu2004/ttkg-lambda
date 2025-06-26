import json
import os
import boto3
import asyncio
from langchain_experimental.graph_transformers import LLMGraphTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

# Remove dotenv import and load_dotenv() call

# Initialize the Secrets Manager client
secretsmanager = boto3.client('secretsmanager')

def get_secret():
    """Get the OpenAI API key from Secrets Manager."""
    secret_name = os.environ.get('SECRET_NAME')
    try:
        response = secretsmanager.get_secret_value(SecretId=secret_name)
        secret = json.loads(response['SecretString'])
        return secret.get('OPENAI_API_KEY')
    except Exception as e:
        # Handle secret-not-found exceptions
        print(f"Error retrieving secret: {e}")
        raise e

# Initialize LLM with the API key from Secrets Manager
# We'll use a lazy initialization pattern to avoid cold start issues
llm = None
llm_transformer = None

def get_llm():
    global llm, llm_transformer
    if llm is None:
        api_key = get_secret()
        llm = ChatOpenAI(temperature=0, model_name="gpt-4-turbo", openai_api_key=api_key)
        llm_transformer = LLMGraphTransformer(llm=llm)
    return llm, llm_transformer

async def extract_kg_from_text_chunk(chunk):
    _, transformer = get_llm()
    document = Document(page_content=chunk)
    graph_document = await transformer.aconvert_to_graph_documents([document])
    return graph_document[0].nodes, graph_document[0].relationships

async def extract_kg_from_text(text):
    """
    Extracts a knowledge graph from the provided text using GPT.
    
    Args:
        text (str): The input text from which to extract the knowledge graph.
        
    Returns:
        tuple: A tuple containing two lists - nodes and relationships.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = splitter.split_text(text)

    all_nodes = []
    all_relationships = []

    # Process each chunk separately
    for chunk in chunks:
        nodes, relationships = await extract_kg_from_text_chunk(chunk)
        all_nodes.extend(nodes)
        all_relationships.extend(relationships)

    # Deduplicate nodes and relationships
    all_nodes = [(n.id, n.type) for n in all_nodes]
    all_relationships = [(r.source.id, r.target.id, r.type) for r in all_relationships]

    return all_nodes, all_relationships

def lambda_handler(event, context):
    """
    Lambda function handler to process the event and extract knowledge graph.
    
    Args:
        event (dict): The event data passed to the Lambda function.
        context (LambdaContext): The context object provided by AWS Lambda.
        
    Returns:
        dict: A response containing the extracted knowledge graph.
    """
    try:
        body = json.loads(event['body'])
        text = body.get('text', '')

        print(event['body'])
        
        if not text:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No text provided"})
            }

        nodes, relationships = asyncio.run(extract_kg_from_text(text))

        return {
            "statusCode": 200,
            "body": json.dumps({
                "nodes": nodes,
                "relationships": relationships
            })
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
