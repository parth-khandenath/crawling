import pandas as pd
import os
# import google_auth_oauthlib.flow
from googleapiclient.discovery import build
import googleapiclient.errors
from dotenv import load_dotenv

load_dotenv()

channel_id='UCQatgKoA7lylp_UzvsLCgcw'   #change here
file_name='yt-trial.csv'    #change here
# apikey_lsts=['AIzaSyAN6JpbgUwqCl1iScIkZxkRrQBYB6zvpd0','AIzaSyDeo9BDSmJcvMLD2oVDlIvF7ONYTbu84nY','AIzaSyD3dhOZFfNt8yXqbUfsINaQ0QrSMlC4-g0','AIzaSyCTYE4tkcLMU1nih0vxvr8uXz_WBJFLfHg','AIzaSyCoRImQPn5kEX1rynV6HUawv5Lropgv1zc','AIzaSyCqqo5Rtfj9_UxJE6uunFCA1bx6DJWIacw','AIzaSyCNgIwxiAh_XF7tmzXx5h9jYD9Ywd-dBDE','AIzaSyAFloRMgEuSodkaIjOwz5u0CmWPAmSbaTU','AIzaSyCGQydk53JSglFM4QmwmhWY4d5faZ0ni2s','AIzaSyB6GEfL2pGdhA1D_1j2yAs77pmRj0iq2eA']
total_api_keys=int(os.getenv('total_api_keys'))
ptr=1
api_key= os.getenv(f'youtube_data_apikey{ptr}') #apikey_lsts[ptr]
youtube =  build('youtube', 'v3', developerKey=api_key)
# playlist_ids=[]
playlist_ids=[channel_id]  #a channel is also a playlist
# next_page_token=None
# request_no=0
# while True:
#     request_no+=1
#     try:
#         request = youtube.playlists().list(part="id,status",channelId=channel_id, maxResults=50,pageToken=next_page_token)
#         response = request.execute()
#     except googleapiclient.errors.HttpError: #quota exceeded
#         print('switching api key')
#         ptr+=1
#         if len(apikey_lsts)==ptr:
#             print("no more api keys...")
#         api_key=apikey_lsts[ptr]
#         youtube =  build('youtube', 'v3', developerKey=api_key)
#         request = youtube.playlists().list(part="id,status",channelId=channel_id, maxResults=50,pageToken=next_page_token)
#         response = request.execute()
#     # print(response)
#     try:
#         next_page_token=response['nextPageToken']
#     except:
#         break
#         # next_page_token=None
#     for ele in response['items']:
#         if ele['status']['privacyStatus']=='public':
#             playlist_ids.append(ele['id'])
#     # if next_page_token==None or len(next_page_token)==0:
#     #     break
# print("total requests:",request_no)
# print(len(playlist_ids))
df_header={
        'title':[],
        'views':[],
        'date':[]
    }
try:
    df=pd.read_csv(file_name)
except:
    df=pd.DataFrame(df_header)

next_page_token=None
video_count=0
for pl_id in playlist_ids:
    while True:
        my_file=open("C:\\Users\\Admin\\Desktop\\pfm\\crawling\\pagefile.txt",'r')
        next_page_token=my_file.read().strip()
        my_file.close()
        if next_page_token=="None":
            next_page_token=None
        print('next page:',next_page_token)
        while True:
            try:    
                youtube =  build('youtube', 'v3', developerKey=api_key)
                request = youtube.playlistItems().list(part="id,snippet,status,contentDetails",maxResults=50,pageToken=next_page_token,playlistId=pl_id)
                response = request.execute()
                break
            except googleapiclient.errors.HttpError: #quota exceeded
                print('switching api key')
                ptr+=1
                if ptr>total_api_keys:
                    print("no more api keys...")
                    break
                else:
                    api_key=os.getenv(f'youtube_data_apikey{ptr}')
        # print("##################")
        # print(len(response['items']))
        for plitem in response['items']:
            if plitem['status']['privacyStatus']=='private': #private video, skip
                continue
            video_count+=1
            video_id=(plitem['contentDetails']['videoId'])
            video_title=(plitem['snippet']['title'])
            video_date=(plitem['snippet']['publishedAt'])
            # video_desc=(plitem['snippet']['description'])
            while True:
                try:
                    youtube =  build('youtube', 'v3', developerKey=api_key)
                    request2 = youtube.videos().list(part="statistics",id=video_id)
                    response2 = request2.execute()
                    break
                except googleapiclient.errors.HttpError: #quota exceeded
                    print('switching api key')
                    ptr+=1
                    if ptr>total_api_keys:
                        print("no more api keys...")
                        break
                    else:
                        api_key=os.getenv(f'youtube_data_apikey{ptr}')
            try:
                views=response2['items'][0]['statistics']['viewCount']  #likes,comments,favourites are also fetchable 
                # if int(views)>100000:  #less views, skip
                df.loc[len(df.index)]=[video_title,views,video_date]
                df.to_csv(file_name,index=False)    
            except Exception as e:
                print(video_id,':',e)
        try:
            next_page_token=response['nextPageToken']
        except Exception as e:
            print('err:',e)
            print(response)
            print("BREAKING......1")
            break
        print("videos done:",video_count)
        my_file=open("C:\\Users\\Admin\\Desktop\\pfm\\crawling\\pagefile.txt",'w')
        my_file.write(str(next_page_token))
        my_file.close()
        if next_page_token==None or len(next_page_token)==0:
            print("BREAKING......2")
            break


# url1=f'https://www.googleapis.com/youtube/v3/channels?id={channel_id}&key={api_key}&part=contentDetails'
# response1=requests.request('GET',url1)
# res1_json=response1.json()
# uploads_ids=[]
# for ele in res1_json['items']:
#     uploads_ids.append(ele['id'])


# def get_views(api_key,video_id):
#     youtube = build('youtube', 'v3', developerKey=api_key)
#     request = youtube.videos().list(part="statistics",id=video_id)
#     response = request.execute()
#     return response['items'][0]['statistics']['viewCount']

# video_ids=[]
# video_titles=[]
# video_dates=[]
# video_descs=[]
# video_no=0
# for upld_id in uploads_ids:
#     request = youtube.playlists().list(
#         part="snippet",
#         channelId="UCQatgKoA7lylp_UzvsLCgcw",
#         maxResults=25
#     )
#     response = request.execute()
#     url2=f'https://www.googleapis.com/youtube/v3/playlistItems?playlistId={upld_id}&key={api_key}&part=snippet&maxResults=50'
#     response2=requests.request('GET',url2)
#     res2_json=response2.json()
#     # print(res2_json)
#     next_page_token=None
#     while True:
#         for video in res2_json['items']:
#             video_no+=1
#             title=video['snippet']['title']
#             date=video['snippet']['publishedAt']
#             desc=video['snippet']['description']
#             idd=video['resourceId']['videoId']
#             views=get_views(idd,api_key)
#             if int(views)>100000:   #change here
#                 df.loc[len(df.index)]=[title,views,date]
#                 df.to_csv('yt-tencent4.csv',index=False)
#         next_page_token=res2_json['nextPageToken']
#         if next_page_token==None or len(next_page_token)==0:
#             break
#     print(video_no)
