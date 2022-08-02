# %%
import pandas as pd 
import boto3
import os
import json 

def upload_map_data(jsonObject,filename,path='docsdata'):

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


fillo = 'input/global_carbon/GCB2021v34_percapita_flat.csv'
#%%

data = pd.read_csv(fillo,encoding='latin-1')

#%%

df = data.copy()
# 'Country', 'ISO 3166-1 alpha-3', 'Year', 
# 'Total', 'Coal', 'Oil', 'Gas', 'Cement', 'Flaring', 'Other'

df.dropna(subset=['Country'], inplace=True)

exclude = ['International Transport', 'Global']

df = df.loc[~df['Country'].isin(exclude)]

listo = []

for country in df['Country'].unique().tolist():
  inter = df.loc[df['Country'] == country].copy()
  inter.sort_values(by=['Year'], ascending=True)

  for col in ['Total', 'Coal', 'Oil', 'Gas', 'Cement', 'Flaring', 'Other']:
    inter[col] = pd.to_numeric(inter[col])
    inter[col].fillna(method='ffill', inplace=True)

  inter = inter.loc[inter['Year'] == inter['Year'].max()]

  listo.append(inter)

cat = pd.concat(listo)

cat = cat[['Country', 'Total', 'Coal', 'Oil', 'Gas', 'Cement', 'Flaring', 'Other']]

cat.rename(columns={"Country": 'name'}, inplace=True)

cat.fillna('', inplace=True)

cat = cat.to_dict(orient='records')


dicto = {'sheets': {'data': cat,
        "settings": [
            {
                "title": "Fossil CO2 emissions by country",
                "subtitle": "Last updated 14 October 2021",
                "footnote": "",
                "source": "Global Carbon Project",
                "boundary": "https://interactive.guim.co.uk/gis/world-110m.json",
                "overlay": "",
                "place": "au"
            }
        ],
        "mapping": [
            {
                "data": "Total",
                "display": "Total",
                "values": "0,  1, 2, 3, 4",
                "colours": "#abd9e9, #ffffbf, #fdae61, #f46d43, #d73027",
                "tooltip": "<strong>Country: </strong> {{name}}<br> <b>{{Total}}%</b> increase",
                "overlay-tooltip": "",
                "scale": "threshold",
                "keyText": "Rental price growth (%) \u27f6",
                "zoomScale": "0",
                "centreLat": "-33",
                "centreLon": "147"
            },
            {
                "data": "Gas",
                "display": "Gas",
                "values": "0,  1, 2, 3, 4",
                "colours": "#abd9e9, #ffffbf, #fdae61, #f46d43, #d73027",
                "tooltip": "<strong>Country: </strong> {{name}}<br> <b>{{Gas}}%</b> increase",
                "overlay-tooltip": "",
                "scale": "threshold",
                "keyText": "Rental price growth (%) \u27f6",
                "zoomScale": "0",
                "centreLat": "-33",
                "centreLon": "147"
            }
        ]}
        }


print(dicto)
# print(p['Country'].unique().tolist())

# #%%
# %%
objecto = json.dumps(dicto)


upload_map_data(objecto,'carbon-global-chloro')