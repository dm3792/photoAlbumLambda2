import json
import boto3
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth


REGION = 'us-east-1'
HOST = 'search-photos-cffinal-rupz65gazpwhpvrtmoyatq3hai.us-east-1.es.amazonaws.com'
INDEX = 'photo'


headers = { "Content-Type": "application/json", "Authorization":"Basic bWFzdGVyOk1EZWxhc3RpY3NlYXJjaDEj" }
client = boto3.client('lexv2-runtime')

def query(term):
    q = {'size': 5, 'query': {'multi_match': {'query': term}}}
    client = OpenSearch(hosts=[{
    'host': HOST,
    'port': 443
    }],
    http_auth=get_awsauth(REGION, 'es'),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection)
    res = client.search(index=INDEX, body=q)
    print(res)
    hits = res['hits']['hits']
    results = []
    for hit in hits:
        results.append(hit['_source'])
    return results
    
def get_awsauth(region, service):
    cred = boto3.Session().get_credentials()
    return AWS4Auth(cred.access_key,
    cred.secret_key,
    region,
    service,
    session_token=cred.token)

def lambda_handler(event, context):
    
    print(event)
    
    msg_from_user = event["queryStringParameters"]["q"]
    print(f"Message from frontend: {msg_from_user}")

    response = client.recognize_text(
        botId='LCFBYMFZMN', # MODIFY HERE
        botAliasId='5NSTDOYLEO', # MODIFY HERE
        localeId='en_US',
        sessionId='testuser',
        text=msg_from_user)
        
    print('printing response')
    print(response)

    q1= response['sessionState']['intent']['slots']['query1']['value']['interpretedValue']
    q2 = None
    if response['sessionState']['intent']['slots']['query2']!=None:
        q2= response['sessionState']['intent']['slots']['query2']['value']['interpretedValue']
    
    print(q1)
    print(q2)
    
    results1 = query(q1)
    print(results1)
    print(type(results1))
    results2=[]
    if q2!=None:
        results2 = query(q2)

    urls = []
    baseurl = 'https://photos-bucket-cf-dm3792.s3.amazonaws.com/'
    
    for item in results1+results2:
        urls.append(baseurl+item['objectKey'])
    
    print(urls)
   
    return {
        'statusCode': 200,
        'headers': {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': '*',
        },
        'body': json.dumps({'urls': urls})
    }
    
