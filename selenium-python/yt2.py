import os
import googleapiclient.discovery
import pandas as pd


# Function to get YouTube channel ID using username
def get_channel_id(api_key, username):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.channels().list(part="id", forUsername=username)
    response = request.execute()
    if 'items' in response:
        return response['items'][0]['id']
    else:
        return None

# Function to fetch all videos of a channel using channel ID
def get_channel_videos(api_key, channel_id):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    videos = []
    next_page_token = None
    while True:
        request = youtube.search().list(
            part="snippet",
            channelId=channel_id,
            maxResults=50,  # Maximum results per page
            order="date",
            pageToken=next_page_token,
            type="video"
        )
        response = request.execute()
        videos.extend(response['items'])
        next_page_token = response.get('nextPageToken')
        if not next_page_token:
            break
    return videos

# Function to extract video details
def extract_video_details(api_key,video):
    title = video['snippet']['title']
    video_id = video['id']['videoId']
    upload_date = video['snippet']['publishedAt']
    views = get_video_views(api_key,video_id)
    return {'title': title, 'upload_date': upload_date, 'views': views}

# Function to get video views using video ID
def get_video_views(api_key,video_id):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.videos().list(part="statistics", id=video_id)
    response = request.execute()
    if 'items' in response and 'statistics' in response['items'][0]:
        return response['items'][0]['statistics'].get('viewCount', 0)
    else:
        return 0

# Main function
def main():
    api_key = 'AIzaSyAN6JpbgUwqCl1iScIkZxkRrQBYB6zvpd0'
    channel_id='UCQatgKoA7lylp_UzvsLCgcw'


    df_header={
        'title':[],
        'views':[],
        'date':[]
    }
    df=pd.DataFrame(df_header)

    if channel_id:
        # Fetch all videos of the channel
        videos = get_channel_videos(api_key, channel_id)

        # Extract video details
        video_details = [extract_video_details(api_key,video) for video in videos]

        # Display video details
        video_no=1
        for video in video_details:
            print('video no:',video_no)
            if int(video['views'])>100000:
                print('taken')
                df.loc[len(df.index)]=[video['title'],video['views'],video['upload_date']]
                df.to_csv('yt-TencentVideo.csv',index=False)
            # print(f"Title: {video['title']}")
            # print(f"Upload Date: {video['upload_date']}")
            # print(f"Views: {video['views']}")
            # print("=" * 30)
        print('total videos:',video_no)
    else:
        print("Channel not found or error in retrieving channel ID.")

if __name__ == "__main__":
    main()
