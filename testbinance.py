import pandas as pd
import requests
import json
import os

api_key = os.getenv('API_KEY')
api_secret = os.getenv('API_SECRET')

url = 'https://api1.binance.com'
# url = https://api.binance.us # for US users

api_call = '/api/v3/ticker/price'

headers = {'content-type': 'application/json', 
           'X-MBX-APIKEY': api_key}

response = requests.get(url + api_call, headers=headers)

response = json.loads(response.text)
df = pd.DataFrame.from_records(response)
df.head()
print(df.head())