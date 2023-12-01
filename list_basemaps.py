import os 
import boto3

if 'AWS_ACCESS_KEY_ID' in os.environ:
    AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
if 'AWS_SECRET_ACCESS_KEY' in os.environ:
    AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

if 'AWS_SESSION_TOKEN' in os.environ:
    AWS_SESSION = os.environ['AWS_SESSION_TOKEN']

session = boto3.Session(
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    aws_session_token = AWS_SESSION
    )

s3 = session.resource('s3')

s3_client = session.client('s3')

response = s3_client.list_objects_v2(Bucket='gdn-cdn', Prefix='gis')

listo = []
for obj in response['Contents']:
    keyo = obj['Key']
    if "ihad-test" not in keyo:
        if keyo.endswith('.json'):

            print(keyo)
            listo.append(keyo)
