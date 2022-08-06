import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime
import os
from googleapiclient.discovery import build

plt.style.use('seaborn')

api_key = os.environ.get('API_KEY') 
uploads_id = 'UUwBtP6NDQtsP5YBa4vuZqHA'
youtube = build('youtube','v3',developerKey=api_key)

view_count = []
like_count = []
title = []
published = []

date_pattern = re.compile(r'(\d+-\d+-\d+)')

nextPageToken = None

while True:
    ch_request = youtube.channels().list(
        part='contentDetails',
        id='UCwBtP6NDQtsP5YBa4vuZqHA'
    )

    ch_response = ch_request.execute()
    #print(ch_response) <-- from here we are taking uploads_id, for better code transparency I stored it in variable


    pl_request = youtube.playlistItems().list(
        part = 'contentDetails',
        playlistId = uploads_id,
        maxResults = 50,
        pageToken = nextPageToken
    )

    pl_response = pl_request.execute()
    #print(pl_response) <-- with this we can access ids of published films 

    vid_ids = []
    for item in pl_response['items']:
        vid_ids.append(item['contentDetails']['videoId'])

    vid_request = youtube.videos().list(
        part='statistics',
        id=','.join(vid_ids)
    )

    vid_response = vid_request.execute()
    #print(vid_response) <-- using that we can see statistics for every uploaded video on channel

    for item in vid_response['items']:
        view_count.append(int(item['statistics']['viewCount']))
        like_count.append(int(item['statistics']['likeCount']))


    title_request = youtube.videos().list(
        part='snippet',
        id=','.join(vid_ids)
    )

    title_response = title_request.execute() # <-- access to titles and published dates
    

    for item in title_response['items']:
        title.append(item['snippet']['title'])
        date_pub = item['snippet']['publishedAt']
        published_at = date_pattern.search(date_pub)
        published_at = published_at.group(1)
        published.append(published_at)
    

    nextPageToken = ch_response.get('nextPageToken')

    if not nextPageToken:
        break

def format_num(data_value, indx):
    formatter = '{:1.1f} MLN'.format(data_value*0.000_001)
    return formatter

def format_num2(data_value, indx):
    formatter = '{:1.1f} K'.format(data_value*0.0001)
    return formatter

avg_likes = sum(like_count)/len(like_count)
avg_views = sum(view_count)/len(view_count)

fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=2)


ax1.axhline(avg_views, color='#6B0504', label='Średnie wyświetlenia')
ax2.axhline(avg_likes, color='#6B0504', label='Średnie  łapki w góre')
ax1.bar(published,view_count,   edgecolor='black', linewidth=1, label='Wyświetlenia', alpha=0.75)
ax2.bar(published, like_count,  color='#E6AF2E',   edgecolor='black', linewidth=1, label='Łapki w góre', alpha=0.75)

ax1.set_title('Filmy Mrożona')
ax2.set_xlabel('Data wstawienia filmu')

plt.gcf().autofmt_xdate()

ax1.set_yticks(np.arange(0, max(view_count)+1, 3_000_000))
ax1.yaxis.set_major_formatter(format_num)
ax2.yaxis.set_major_formatter(format_num2)

fig.legend(loc=('upper right'), frameon=True)
plt.tight_layout()
plt.show()

