import json
#import elasticsearch
#from elasticsearch import Elasticsearch, RequestsHttpConnection
import requests
from requests_aws4auth import AWS4Auth
from datetime import datetime
import boto3
# import elasticsearch.helpers

def indexData(photo,bucket,labels):
    host = 'https://search-photos-2-juhvlikuvirrvtesky3hpdkoxa.us-east-1.es.amazonaws.com/'
    path = 'photos-2/photo'
    region = 'us-east-1' 
    
    
    service = 'es'
    credentials = boto3.Session().get_credentials()
   
    awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, service, session_token=credentials.token)
    # es = Elasticsearch(
    #     hosts = [{'host': host, 'port': 443}],
    #     http_auth = awsauth,
    #     use_ssl = True,
    #     verify_certs = True,
    #     connection_class = RequestsHttpConnection
    # )
    
    date_timestamp = datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    url = host + path
    print("date", date_timestamp)
    headers = {'Content-Type':'application/json'}
    
    document = {
        'objectKey': photo,
        'bucket': bucket,
        'createdTimestamp': date_timestamp,
        'labels': labels
    }
    print("doc: ", document)
    
    # es.index(index="photos", doc_type="_doc", id=date_timestamp, body=document)
    r = requests.post(url, data=json.dumps(document), headers=headers, auth=awsauth)
    print("status :", r)
    
    # print(es.get(index="photos", doc_type="_doc", id=date_timestamp))
    print("elasticsearch: ", r.text)
    
    # es_response = elasticsearch.helpers.scan(es,
    #     index='photos',
    #     doc_type='_doc',
    #     query={"query": { "match_all" : {}}}
    # )

    # for item in es_response:
    #     print(json.dumps(item))

def detectLables(photo,bucket):
    print("calling detect label function")
    labels_detected=[]
    client=boto3.client('rekognition','us-east-1')
    print ("rekognition-client: ", client)
    result = client.detect_labels(Image={'S3Object':{'Bucket':bucket,'Name':photo}}, MaxLabels=10, MinConfidence=90)
    print("result",result)
    for label in result['Labels']:
        labels_detected.append(label['Name'])
    return labels_detected

def lambda_handler(event, context):
    print(event)
    for entry in event['Records']:
        bucket=entry['s3']['bucket']['name']
        photo=entry['s3']['object']['key']
        print("bucket-name: ",bucket)
        print("photo-key: ",photo)
        labels= detectLables(photo,bucket)
        print("labels",labels)
        indexData(photo,bucket,labels)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
    
