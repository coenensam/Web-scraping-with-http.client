# -*- coding: utf-8 -*-
"""
Created on Fri May 24 13:04:19 2024

@author: sam37
"""

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import numpy as np
import time

#######################################

# Using http.client

import http.client
import json

# Set up connection
conn = http.client.HTTPSConnection('www.sofascore.com')

# Headers and cookies
headers = {
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'cache-control': 'max-age=0',
    'cookie': '_gcl_au=1.1.1288433488.1716398667; _ga=GA1.1.1194105875.1716398669; FCCDCF=%5Bnull%2Cnull%2Cnull%2C%5B%22CP_BBcAP_BBcAEsACBENA1EoAP_gAEPgAA6II3gB5C5ETSFBYH51KIsUYAEHwAAAIsAgAAYBAQABQBKQAIQCAGAAEAhAhCACgAAAIEYBIAEACAAQAAAAAAAAIAAEIAAQAAAIICAAAAAAAABIAAAIAAAAEAAAwCAABAAA0AgEAJIISMgAAAAAAAAAAgAAAAAAAgAAAEhAAAEIAAAAACgAEABAEAAAAAEIABBII3gB5C5ETSFBYHhVIIMUIAERQAAAIsAgAAQBAQAAQBKQAIQCEGAAAAgAACAAAAAAIEQBIAEAAAgAAAAAAAAAIAAEAAAAAAAIICAAAAAAAABAAAAIAAAAAAAAwCAABAAAwQhEAJIASEgAAAAgAAAAAoAAAAAAAgAAAEhAAAEAAAAAAAAAEAAAEAAAAAAAABBIAAA.dnAACAgAAAA%22%2C%222~41.70.89.108.149.211.313.358.415.486.540.621.981.1029.1046.1092.1097.1126.1205.1301.1516.1558.1584.1598.1651.1697.1716.1753.1810.1832.1985.2328.2373.2440.2571.2572.2575.2577.2628.2642.2677.2767.2860.2878.2887.2922.3182.3190.3234.3290.3292.3331.10631~dv.%22%2C%22B315CD21-42CF-479E-9690-76340766A52E%22%5D%5D; _ga_3KF4XTPHC4=deleted; __gads=ID=066580bb9e47a032:T=1716398678:RT=1717964552:S=ALNI_MYMJ7zi9Rv1Ppj0kcXepXtIoIdNqg; __gpi=UID=00000e28926f6eee:T=1716398678:RT=1717964552:S=ALNI_MbbiKzlZdFtlQkAVeRmWduXuIuJQg; __eoi=ID=0911a3322fb7cce9:T=1716398678:RT=1717964552:S=AA-Afjbk-Y9tiW1fR53HpeI37td8; FCNEC=%5B%5B%22AKsRol-K0NTjXgkGNlCRddD58vfhKWqNINRiwBlDTqD5fcXh2wrEcn53pRvZuoTAiuENsh2J9IA3dr99lLYKl8VQ6oQ_S-GXHiPvh3Ss1Jf7yJEWyiXMK61zHmbF6RZtjkT0jCUERdGmYkXvpriRi8TcwsxyDXvs0w%3D%3D%22%5D%5D; _ga_QH2YGS7BB4=GS1.1.1717964327.43.1.1717964711.0.0.0; _ga_3KF4XTPHC4=GS1.1.1717964328.43.1.1717964711.60.0.0; _ga_HNQ9P9MGZR=GS1.1.1717964328.42.0.1717964711.60.0.0',
    'if-none-match': 'W/"4bad0119b3"',
    'referer': 'https://www.sofascore.com/tennis/2024-06-03',
    'sec-ch-ua': '"Opera GX";v="109", "Not:A-Brand";v="8", "Chromium";v="123"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 OPR/109.0.0.0 (Edition std-1)',
    'x-requested-with': 'f92bd3',
}
headers['if-none-match']=''

########################################

""" Find all matches in a day, store the match id, the winner, the start time
and the players."""

# Make the request
conn.request('GET', '/api/v1/sport/tennis/scheduled-events/2024-06-03', headers=headers)

# Get the response
response = conn.getresponse()
data = response.read()
data_json = json.loads(data.decode('utf-8'))

df = {'match_id':[],
      'players':[],
      'winner':[],
      'start timestamp':[],
      }

for event in data_json['events']:
    if 'winnerCode' in event.keys():
        df['winner'].append(event['winnerCode'])
        df['match_id'].append(event['id'])
        df['players'].append(event['slug'])
        df['start timestamp'].append(event['startTimestamp'])
        
df = pd.DataFrame(df)        
df = df.set_index('match_id')

conn.close()

####################################

""" Find all matches in the span between two days, store the match id,
the winner, the start time and the players."""

dates = pd.date_range('2024-01-02','2024-06-03').date

dfs = []

for date in dates:
    
    # Make the request
    conn.request(
        'GET', '/api/v1/sport/tennis/scheduled-events/{}'.format(date),
        headers=headers
        )
    
    # Get the response
    response = conn.getresponse()
    data = response.read()
    data_json = json.loads(data.decode('utf-8'))
    
    for event in data_json['events']:
        if 'winnerCode' in event.keys():
            dfs.append({
                'winner':event['winnerCode'],
                'match_id':event['id'],
                'players':event['slug'],
                'start timestamp':event['startTimestamp']
                })
    
df = pd.DataFrame(dfs)        
df = df.set_index('match_id')
df = df.drop_duplicates()

conn.close()

#####################################

"""Get odds for all matches in df"""

# Get odds
def odd_converter(odd):
    
    try:
    
        split_odd = odd.split('/')
        return (int(split_odd[0])+int(split_odd[1]))/int(split_odd[1])
    
    except:
        
        return np.nan

odd_home = []
odd_away = []

for matchid in df.index:
    
    try:
        conn.request('GET', '/api/v1/event/{}/odds/1/featured'.format(matchid), headers=headers)    

        response = conn.getresponse()
        data = response.read()
        data_json = json.loads(data.decode('utf-8'))
        
        odd1 = data_json['featured']['fullTime']['choices'][0]['fractionalValue']
        odd2 = data_json['featured']['fullTime']['choices'][1]['fractionalValue']
        
        odd_home.append(odd_converter(odd1))
        odd_away.append(odd_converter(odd2))
     
        # if len(odd_home)!=len(odd_away):
        #     break
    
    except:
        odd_home.append(np.nan)
        odd_away.append(np.nan)
    
conn.close()
    
df['odd home'] = odd_home
df['odd away'] = odd_away
    
####################################

"""Get votes for all matches in df"""

votes1=[]
votes2=[]

for matchid in df.index:

    conn.request('GET', '/api/v1/event/{}/votes'.format(matchid), headers=headers)    

    response = conn.getresponse()
    data = response.read()
    data_json = json.loads(data.decode('utf-8'))
    
    votes1.append(data_json['vote']['vote1'])
    votes2.append(data_json['vote']['vote2'])
    
conn.close()

df['votes home'] = votes1
df['votes away'] = votes2

######################################

"""Data analysis"""

df['impl prob home'] = 1/df['odd home']
df['impl prob away'] = 1/df['odd away']
df['total votes'] = df['votes home']+df['votes away']
df['votes prob home'] = df['votes home']/df['total votes']
df['votes prob away'] = df['votes away']/df['total votes']

# Partition the data based on the probability of home victory implied by votes
# into 5% bins
bins = np.arange(0,1.05,0.05)

df['bin'] = pd.cut(df['votes prob home'], bins, include_lowest=True)

# Take matches with more than 500 votes
df_tot_votes = df[df['total votes']>500]

# Find mean probabilities and mean odds in each bin
probs_per_bin = df_tot_votes.groupby('bin').apply(lambda x: pd.Series({
    'prob votes': x['votes prob home'].mean(),
    'prob outcomes':(x['winner']==1).sum()/len(x),
    'population': len(x),
    'prob odd': x['impl prob home'].mean(),
    'avg odd away':x['odd away'].mean(),
    'avg odd home':x['odd home'].mean()
    }))

# Take matches were there is a big difference between prob implied by votes
# and prob implied by odds
temp = df_tot_votes[
    abs(df_tot_votes['votes prob home']-df_tot_votes['impl prob home'])/
    df_tot_votes['impl prob home']>0.30]

# Take matches where votes overestimate the probability of home victory
overest_home = temp[(temp['votes prob home']>temp['impl prob home']) & 
                    (temp['votes prob home']>0.6)]

# Test strategy
earnings_strat1 = overest_home[
    overest_home['winner']==1]['odd home'].sum()/len(overest_home)

