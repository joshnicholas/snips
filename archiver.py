# %%

import savepagenow
import pandas as pd 
import random 
import time 

import datetime
import pytz

utc_now = pytz.utc.localize(datetime.datetime.utcnow())
bris_now = utc_now.astimezone(pytz.timezone("Australia/Brisbane"))

from sudulunu.helpers import dumper, pp 

def rand_delay(num):
  
  rando = random.random() * num
  print(rando)
  time.sleep(rando)

# %%



links = [
]


# %%

records = []

for linko in links:
    try:
        archiver = savepagenow.capture_or_cache(linko)

        record = {"Original": linko, "Saved": archiver[0], 'Captured': bris_now}

        records.append(record)

        # print(archiver)

        rand_delay(1)
    except Exception as e:
       print(e)
       continue

    df = pd.DataFrame.from_records(records)

    # print(df)
    # print(records)

    dumper('inter', 'report_archive', df)



# %%

# %%
