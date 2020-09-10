#TODO: Add tracer import
import appdynamics

import json
from faker import Faker
import boto3
import uuid
import os
from random import randint

#TODO: Add in AppDynamics tracer decorator
@appdynamics.tracer
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
            #TODO: Add in error reporting.
            appdynamics.report_error(error_name="No records found", error_message="No records found.")

            retval = {
                "statusCode" : 404,
                "body" : None
            }
        elif randint(1, 100) == 74:       
            #TODO: Add in error reporting.
            appdynamics.report_error(error_name="Unknown", error_message="Unknown Error in Lambda Handler")

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

        #TODO: Add in S3 exit call
        with appdynamics.ExitCallContextManager(exit_point_type="CUSTOM", exit_point_subtype="Amazon Web Services", identifying_properties={"VENDOR": "S3", "BUCKET_NAME" : os.environ["CANDIDATE_S3_BUCKET"]}) as ec:
            try:
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
            except Exception as e:

                #TODO: Add in S3 exit call error reporting
                ec.report_exit_call_error(error_name=type(e).__name__, error_message=e)
                body = {
                    "message": "Could not upload resume."
                }

                retval = {
                    "statusCode": 500,
                    "body": json.dumps(body)
                }       

    return retval
