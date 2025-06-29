import json

def health_check(event, context):
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