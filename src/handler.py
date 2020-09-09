import json
from faker import Faker
import boto3
import uuid
import os
from random import randint

def lambda_function(event, context):
    retval = {}

    if event['path'] == "/resume/random":
        lambda_client = boto3.client('lambda')
        response = lambda_client.invoke(
            FunctionName = context.function_name.replace("lambda-1", "lambda-2"),
            InvocationType = 'RequestResponse'
        )

        responsePayload = response['Payload'].read().decode('utf-8')        

        if responsePayload is None:
            retval = {
                "statusCode" : 404,
                "body" : None
            }
        elif randint(1, 100) == 74:
            retval = {
                "statusCode" : 500,
                "body" : "Unknown Error"
            }
        else:
            retval = {
                "statusCode" : 200,
                "body" : responsePayload
            }
    else:
        faker = Faker()

        profile = json.dumps(faker.profile(["job", "company", "ssn", "residence", "username", "name", "mail"]))
        key = uuid.uuid4().hex + ".json"

        s3_client = boto3.client('s3')
        s3_client.put_object(Body=profile, Bucket=os.environ["CANDIDATE_S3_BUCKET"], Key=key)

        body = {
            "message": "Uploaded successfully.",                    
            "file" : key
        }

        retval = {
            "statusCode": 201,
            "body": json.dumps(body)
        }

    return retval

def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response

    # Use this code if you don't use the http event with the LAMBDA-PROXY
    # integration
    """
    return {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "event": event
    }
    """
