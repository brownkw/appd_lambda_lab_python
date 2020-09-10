#TODO: Add tracer import
import appdynamics 
import json
from random import randint
import boto3
import os

#TODO: Add in AppDynamics tracer decorator
@appdynamics.tracer
def lambda_function(event, context):

    s3_client = boto3.client('s3')
    response = None
    objs = None 
    idx = -1
    obj_key = ""
    obj = None
    obj_contents = None

    #TODO: Add in S3 exit call
    with appdynamics.ExitCallContextManager(exit_point_type="CUSTOM", exit_point_sub_type="Amazon Web Services", identifying_properties={"VENDOR": "S3", "BUCKET NAME" : os.environ["CANDIDATE_S3_BUCKET"]}) as ec:
        objs = s3_client.list_objects_v2(Bucket = os.environ["CANDIDATE_S3_BUCKET"])['Contents']

    idx = randint(0, len(objs) - 1)

    obj_key = objs[idx]['Key']    
    with appdynamics.ExitCallContextManager(exit_point_type="CUSTOM", exit_point_sub_type="Amazon Web Services", identifying_properties={"VENDOR": "S3", "BUCKET NAME" : os.environ["CANDIDATE_S3_BUCKET"]}) as ec:
        obj = s3_client.get_object(Bucket = os.environ["CANDIDATE_S3_BUCKET"], Key = obj_key)
    
    obj_contents = json.loads(obj['Body'].read().decode('utf-8'))

    response = {
        "file" : obj_key,
        "contents" : obj_contents
    }

    if randint(1, 100) == 74:
        response = None

    return response
