# %%
import pandas as pd 

import requests
#from bs4 import BeautifulSoup as bs å

import datetime 
import pytz

import os 
import pathlib

# %%


##
def dumper(path, name, frame):
    with open(f'{path}/{name}.csv', 'w') as f:
        frame.to_csv(f, index=False, header=True)

##
def rand_delay(num):
  import random 
  import time 
  rando = random.random() * num
  print(rando)
  time.sleep(rando)

##
def check_if_there(pathos, to_check):
    if pathos[-1] != '/':
        pathos += '/'

    folds = os.listdir(pathos)

    if to_check not in folds:
        os.mkdir(f"{pathos}{to_check}")
    

# %%

today = datetime.datetime.now()
scrape_date_stemmo = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%Y%m%d')
scrape_hour = today.astimezone(pytz.timezone("Australia/Brisbane")).strftime('%H')

# %%

pathos = pathlib.Path(__file__).parent
os.chdir(pathos)

#%%

headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36",
'Accept-Language': "en-GB,en-US;q=0.9,en;q=0.8",
"Referer": 'https://www.google.com',
"DNT":'1'}


#%%

### Do initial scrape to get numbers

urlo = ''

r = requests.get(urlo, headers = headers)

#soup = bs(r.text, 'html.parser')

#%%

print(r.text)
print(r.status_code)
# %%
