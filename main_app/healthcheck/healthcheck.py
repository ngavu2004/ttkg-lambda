import json

def health_check(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "healthy server",
        }),
    }