import json
import base64
from os import environ
import logging
import boto3
import requests
from requests_aws4auth import AWS4Auth
from botocore.exceptions import ClientError
import re

region = 'us-east-1' # e.g. us-west-1
service = 'es'
credentials = boto3.Session().get_credentials()
#awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)

host = 'https://search-photos-1-n6ybbsrgoa7st2wj2t53mj3oai.us-east-1.es.amazonaws.com' # the OpenSearch Service domain, e.g. https://search-mydomain.us-west-1.es.amazonaws.com
index = 'photo'
datatype = '_doc'
url = host + '/' + index + '/' + datatype


s3 = boto3.client('s3')

logger = logging.getLogger(__name__)

rek_client = boto3.client('rekognition')

def detect_labels(photo, bucket):
    
    response = rek_client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}},
    MaxLabels=10,
    )

    labels=[]
    for label in response['Labels']:
        labels.append(label['Name'])

    return labels



def lambda_handler(event, context):
   
    
    #TODO: add custom labels from fromtend metadata
    
    print('processing')
    s3obj = boto3.client('s3').head_object(Bucket=event['Records'][0]['s3']['bucket']['name'],Key=event['Records'][0]['s3']['object']['key'])
    #x = boto3.client('s3').head_object(Bucket='projb2',Key='cute12.jpeg')
    print('printing x')
    print(s3obj)
    print("last modified",s3obj['ResponseMetadata']['HTTPHeaders']['last-modified'])
    headers = { "Content-Type": "application/json", "Authorization":"Basic bWFzdGVyOk1EZWxhc3RpY3NlYXJjaDEj" }
    print('event')
    print(event)
    lab = detect_labels(event['Records'][0]['s3']['object']['key'],event['Records'][0]['s3']['bucket']['name'])
    print(lab)

    try: 
        customLabels=s3obj['ResponseMetadata']['HTTPHeaders']['x-amz-meta-customlabels'].split(',')
        print('custom labels')
        print(customLabels)
    except:
        customLabels=[]
    print(headers)
    document = { "objectKey": event['Records'][0]['s3']['object']['key'],
                "bucket": event['Records'][0]['s3']['bucket']['name'],
                "createdTimestamp": s3obj['ResponseMetadata']['HTTPHeaders']['last-modified'] ,
                "labels": customLabels+lab }
    
    r = requests.post(url, json=document, headers=headers)
    print(r)
    
    #return respomns
    
    

    


