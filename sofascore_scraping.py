import http.client
import json
import pandas as pd
import numpy as np
import time

########################################

# Set up connection
conn = http.client.HTTPSConnection('www.sofascore.com')

# Headers and cookies
"""Use appropriate header to access the website"""
headers = {}

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

########################################

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

########################################

"""Get odds for all matches in df"""

# Function that converts fractional odds into decimal odds
def odd_converter(odd):
    
    try:
    
        split_odd = odd.split('/')
        return (int(split_odd[0])+int(split_odd[1]))/int(split_odd[1])
    
    except:
        
        return np.nan

odd_home = []
odd_away = []

# For each match in the dataset, store odds for home victory and away victory
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
    
    except:
        odd_home.append(np.nan)
        odd_away.append(np.nan)
    
conn.close()
    
df['odd home'] = odd_home
df['odd away'] = odd_away
    
########################################

"""Get votes for all matches in df"""

votes1=[]
votes2=[]

# For all matches in the dataset, store the user votes for home victory and away victory
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

########################################

"""Data analysis"""

# Calculate the probabilities implied by the odds ('impl prob') and by the 
# votes ('votes prob')
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

# Take matches were there is a large relative difference between probalities
# implied by votes and probabilities implied by odds
large_diff = df_tot_votes[
    abs(df_tot_votes['votes prob home']-df_tot_votes['impl prob home'])/
    df_tot_votes['impl prob home']>0.30]

# Take matches where votes imply an higher probability than odds for
# home victory
overest_home = large_diff[(large_diff['votes prob home']>large_diff['impl prob home'])]


