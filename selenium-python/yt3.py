from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
import pandas as pd

# Replace 'YOUR_API_KEY' and 'CHANNEL_ID' with your actual API key and channel ID
API_KEY = 'AIzaSyAN6JpbgUwqCl1iScIkZxkRrQBYB6zvpd0'

# Create a YouTube service object
youtube = build('youtube', 'v3', developerKey=API_KEY)
# request = youtube.search().list(
#                         part="snippet",
#                         q="TencentVideo",
#                         type="video",
#                         maxResults=10,
#                         pageToken=None
#                 )
# response = request.execute()

# items = response['items']

# # for item in items:
# #     channel_name = item['snippet']['channelTitle']
# channel_id = items[0]['snippet']['channelId']
# print("ch_id:",channel_id)
channel_id='UCQatgKoA7lylp_UzvsLCgcw'


df_header={
    'title':[],
    'views':[],
    'date':[]
}
df=pd.DataFrame(df_header)

def fetch_all_videos():
    try:
        next_page_token = None
        videos_count = 0

        while True:
            # Retrieve videos from the channel
            request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,  # Adjust the number of videos to retrieve per request
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                if item['id']['kind'] == 'youtube#video':
                    video_title = item['snippet']['title']
                    video_date = datetime.strptime(item['snippet']['publishedAt'], "%Y-%m-%dT%H:%M:%SZ").date()
                    video_id = item['id']['videoId']

                    # Retrieve statistics for each video (including view count)
                    video_stats = youtube.videos().list(
                        id=video_id,
                        part='statistics'
                    ).execute()

                    video_views = video_stats['items'][0]['statistics']['viewCount']
                    print(video_views)
                    if int(video_views)>100000:  #change herer
                        print(video_title)
                        print(video_views)
                        print(video_date)
                        df.loc[len(df.index)]=[video_title,video_views,video_date]
                        df.to_csv('yt-TencentVideo.csv',index=False)
                    # print(f"Title: {video_title}")
                    # print(f"Views: {video_views}")
                    # print(f"Upload Date: {video_date}")
                    # print("------")

                    videos_count += 1
            print(next_page_token)
            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break

        print(f"Total videos found: {videos_count}")
        

    except HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred: {e.content}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

# Call the function to fetch all videos
fetch_all_videos()
