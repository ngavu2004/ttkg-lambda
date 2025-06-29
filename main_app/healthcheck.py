import json

def health_check(event, context):
    # Handle CORS preflight request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type, X-Api-Key",
                "Access-Control-Allow-Methods": "GET, OPTIONS"
            },
            "body": ""
        }
    
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type, X-Api-Key",
            "Access-Control-Allow-Methods": "GET, OPTIONS"
        },
        "body": json.dumps({
            "message": "healthy server",
        }),
    }