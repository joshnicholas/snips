import boto3
import os
import json 

def upload_map(data_path,path,filename):

  with open(data_path, 'r') as f:
    data = json.load(f)

  jsonObject = json.dumps(data)

  if 'AWS_ACCESS_KEY_ID' in os.environ:
    AWS_KEY = os.environ['AWS_ACCESS_KEY_ID']
  if 'AWS_SECRET_ACCESS_KEY' in os.environ:
    AWS_SECRET = os.environ['AWS_SECRET_ACCESS_KEY']

  if 'AWS_SESSION_TOKEN' in os.environ:
    AWS_SESSION = os.environ['AWS_SESSION_TOKEN']

  print("Connecting to S3")
  bucket = 'gdn-cdn'

  if 'AWS_SESSION_TOKEN' in os.environ:
    session = boto3.Session(
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    aws_session_token = AWS_SESSION
    )
  else:
    session = boto3.Session(
    aws_access_key_id=AWS_KEY,
    aws_secret_access_key=AWS_SECRET,
    )

  s3 = session.resource('s3')

  key = "{path}/{filename}.json".format(path=path, filename=filename)
  object = s3.Object(bucket, key)
  object.put(Body=jsonObject, CacheControl="max-age=30", ACL='public-read', ContentType="application/json")

  print("JSON is updated")
  print("data", "https://interactive.guim.co.uk/{path}/{filename}.json".format(path=path, filename=filename))




### Path to the file on your computer:

pathos = 'input/countries-110m.json'

### Path to the file on the server:

end_pathos = 'gis'

### Name of the file:

nammo = 'world-110m'



upload_map(pathos, end_pathos, nammo)