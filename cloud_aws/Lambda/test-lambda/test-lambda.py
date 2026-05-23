import json

def lambda_handler(event, context):
    print('Hello DevSecops students')
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }