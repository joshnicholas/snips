# %%
import requests
import json 

import pandas as pd 

from bs4 import BeautifulSoup as bs

from sudulunu.helpers import dumper, pp, rand_delay

import os 
import pathlib

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

import dateparser

# print(os.getcwd())

keyo = ''

# %%

urlo = f'https://content.guardianapis.com/search?tag=news%2Fseries%2Fthe-crunch-data-newsletter-email&q=the-crunch-data-newsletter-email&api-key={keyo}'

r = requests.get(urlo)



# print(r.text)
# %%

jsony = json.loads(r.text)

# print(jsony['response'].keys())

# print(jsony['response']['results'])

# print(type(jsony['response']['results']))

records = []

for result in jsony['response']['results']:

    # print(result.keys())
    # dict_keys(['id', 'type', 'sectionId', 'sectionName', 'webPublicationDate', 
    # 'webTitle', 'webUrl', 'apiUrl', 'isHosted', 'pillarId', 'pillarName'])

    # print(result['apiUrl'])

    new_r = requests.get(f"{result['apiUrl']}?api-key={keyo}&show-fields=body")

    # new_r = requests.get(f"{result['webUrl']}&show-fields=body")

    new_jsony = json.loads(new_r.text)

    body = new_jsony['response']['content']['fields']['body']

    soup = bs(body, 'html.parser')

    aas = soup.find_all('a')
    urls = list(set([x['href'] for x in aas]))

    datto = dateparser.parse(new_jsony['response']['content']['webPublicationDate']).strftime("%Y-%m-%d")

    # print(datto)
    for url in urls:

        record = {"Date": datto,
        "Newsletter": result['webUrl'],
        "Link": url}
        records.append(record)


    cat = pd.DataFrame.from_records(records)
    cat.drop_duplicates(subset=["Newsletter", "Link"], inplace=True)

    dumper('data', 'scraped', cat)
    rand_delay(1)

# %%
