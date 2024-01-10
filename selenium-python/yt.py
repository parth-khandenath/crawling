from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import pandas as pd

# Replace 'YOUR_API_KEY' and 'CHANNEL_ID' with your actual API key and channel ID
API_KEY = 'AIzaSyAN6JpbgUwqCl1iScIkZxkRrQBYB6zvpd0'
CHANNEL_ID = 'UCQatgKoA7lylp_UzvsLCgcw'

# Create a YouTube service object
youtube = build('youtube', 'v3', developerKey=API_KEY)
df_header={
    'title':[],
    'views':[],
    'date':[]
}
df=pd.DataFrame(df_header)
try:
    # Retrieve the playlist ID of the uploaded videos
    channel_response = youtube.channels().list(id=CHANNEL_ID, part='contentDetails').execute()
    playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    next_page_token = None
    videos_count = 0

    # Iterate through all pages of the playlist to retrieve all videos
    while True:
        playlist_items = youtube.playlistItems().list(
            playlistId=playlist_id,
            part='snippet',
            maxResults=50,  # Adjust the number of videos to retrieve per request
            pageToken=next_page_token
        ).execute()

        videos = playlist_items['items']
        video_no=1
        for video in videos:
            video_title = video['snippet']['title']
            video_date = datetime.strptime(video['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").date()
            video_id = video['snippet']['resourceId']['videoId']

            # Retrieve statistics for each video (including view count)
            video_stats = youtube.videos().list(
                id=video_id,
                part='statistics'
            ).execute()

            video_views = video_stats['items'][0]['statistics']['viewCount']
            print('video count:',videos_count)
            if int(video['views'])>100000:
                print('taken')
                df.loc[len(df.index)]=[video['title'],video['views'],video['upload_date']]
                df.to_csv('yt-TencentVideo1.csv',index=False)
            # print(f"Title: {video_title}")
            # print(f"Views: {video_views}")
            # print(f"Upload Date: {video_date}")
            # print("------")

            videos_count += 1

        next_page_token = playlist_items.get('nextPageToken')

        if not next_page_token:
            break

    print(f"Total videos found: {videos_count}")

except HttpError as e:
    print(f"An HTTP error {e.resp.status} occurred: {e.content}")
except Exception as e:
    print(f"An error occurred: {str(e)}")
