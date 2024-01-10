import json
import time
import math
import os
import requests
import re
import datetime
from time import sleep
import warnings
from datetime import datetime
from requests import Session
import logging
from docx import Document
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

#general imports
from novels_cron.cms.task_scheduler.task_scheduler import TaskProcessor
from novels_cron.cms.task_scheduler.utills import TaskTypes, TaskStatus, RemarkTypes
from novels_cron.helpers import LOG_FORMAT, get_hash_key,get_database_connection
from novels_cron.utils import S3

#youtube API imports
import googleapiclient
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

logging.basicConfig(filename='youtube_crawler.log', format=LOG_FORMAT)
log = logging.getLogger("youtbubeCrawlerDump")
log.setLevel(logging.DEBUG)

def run(*args, **kargs):
    log.info("Starting the youtube crawling")


class Youtube(TaskProcessor):
    def __init__(self, task_type):
        super().__init__(task_type)
        self.document = None
        self.final_output = None
        self.search_name = None

    def get_recent_tasks(self):
        CURRENT_TIME = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        db = get_database_connection(mode="read")
        cursor = db.cursor()
        fetch_tasks_query = f"""SELECT * FROM task_scheduler WHERE create_time >= '{CURRENT_TIME}' - INTERVAL 1 DAY 
                                AND status in ('pending','failed') AND task_type='{self.task_type}' order by create_time desc"""
        cursor.execute(fetch_tasks_query)

        self.tasks = cursor.fetchall()
        cursor.close()
    
    def update_task_status(self):
        db = get_database_connection()
        cursor = db.cursor()
        file_url = 'NULL'
        if self.url:
            file_url = f"'{self.url}'"
        q = f"""UPDATE task_scheduler SET status ='{self.task_status}', file_url={file_url} 
                WHERE task_id = '{self.task_id}'"""
        cursor.execute(q)
        db.commit()


    def process_all_tasks(self):
        for task in self.tasks:
            self.task_id = task[0]
            log.info(f"Working on Task id: {self.task_id}")
            props = json.loads(task[7])

            try:
                self.process_content(props)
            except Exception as e:
                log.info(f"Task {self.task_id}: Failed in the process content Method .... Error: {str(e)}")
                self.task_status = TaskStatus.REJECTED.value
                self.url = None

            self.update_task_status()

    
    def process_content(self,props):
        search_name = props['search_name'] # only single string "Search Query"
        self.search_name = search_name

        start_date = self.date_time_converter(props['start_date'])

        end_date = ''
        if props['end_date'] == '':
            end_date = datetime.datetime.now()
        else:
            end_date = self.date_time_converter(props['end_date'])

        final_output = self.youtube_api_fetch_data(search_name, start_date, end_date)

        self.document = final_output
        self.url = self.upload_document_to_s3()
        self.task_status = TaskStatus.COMPLETED.value
        if not self.url:
            self.task_status = TaskStatus.REJECTED.value


    def upload_document_to_s3(self):
        if not isinstance(self.document,pd.DataFrame):
            return None
        
        today = datetime.now()
        today = today.strftime("%m-%d-%Y-%H-%M-%S")
        key = f"{self.search_name}_{today}"
        filename = self.search_name + "_" + today + "_" + get_hash_key(key.encode("utf-8")) + ".csv"
        
        self.document.to_csv(filename)
        
        bucket = "radiolycontent"
        destination_file_path = "youtube_crawl_file/" + filename
        s3 = S3()
        pre_signed_url_cdn = None
        try:
            s3.upload_public_read_file(filename, bucket, destination_file_path)
            pre_signed_url_cdn = "https://d3mg5si48756ug.cloudfront.net/" + filename
            os.remove(filename)
        except Exception as e:
            log.exception(f"Pdf File upload to s3 failed with error - {str(e)}")
        
        return pre_signed_url_cdn

    def date_time_converter(self ,date_string):
        #format of Input: eg: "18 Apr 2023" 
        #format of Ouptut, eg: "2023-04-18T00:00:00Z"
        date_obj = datetime.strptime(date_string, '%d %b %Y')
        year = date_obj.strftime('%Y')
        month = date_obj.strftime('%m')
        day = date_obj.strftime('%d')
        output_format = '%Y-%m-%dT%H:%M:%SZ'
        output_string = f"{year}-{month}-{day}T00:00:00Z"
        output_date_obj = datetime.strptime(output_string, output_format)
        output_date_string = output_date_obj.strftime(output_format)

        return output_date_string

    def youtube_api_fetch_data(self,search_name, start_date, end_date):
        api_service_name = "youtube"
        api_version = "v3"

        warnings.simplefilter(action='ignore', category=FutureWarning)

        SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

        api_key = os.getenv("youtube_data_apikey")#"AIzaSyDu5vZooYwwFuPk1IRhyAJfGoYiouq2aR4"
        youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

        page_token = None

        df = pd.DataFrame() #to store the output

        try:
            counter=0
            while True:
                counter+=1
                request = youtube.search().list(
                        part="snippet",
                        q=search_name,
                        type="video",
                        maxResults=50,
                        pageToken=page_token,
                        publishedBefore= end_date,
                        publishedAfter = start_date
                )
                response = request.execute()
                
                items = response['items']

                for item in items:
                    channel_name = item['snippet']['channelTitle']
                    ch_id = item['snippet']['channelId']
                    video_id = item['id']['videoId']
                    url = f'https://www.youtube.com/watch?v={video_id}'
                    req = requests.get(url)
                    text = req.text

                    #length
                    video_length = ''
                    try:
                        video_length_expression = re.findall(r'"lengthSeconds":".*?"', text)
                        video_length = video_length_expression[0].replace('"lengthSeconds":"','')
                        video_length = video_length.replace('"','')
                    except:
                        pass

                    #title
                    title_expression=''
                    try:
                        title_expression = re.findall(r'"title":{"simpleText":".*?"}', text)
                        title = title_expression[0].replace('"title":{"simpleText":"','')
                        title = title.replace('"}','')
                    except:
                        pass

                    views = ''
                    try:
                        views_expression = re.findall(r'"viewCount":{"videoViewCountRenderer":{"viewCount":{"simpleText":".*? views"}', text)
                        views = views_expression[0].replace('"viewCount":{"videoViewCountRenderer":{"viewCount":{"simpleText":"','')
                        views = views.replace(' views"}','')
                        if len(views)>30:
                            views='1'
                    except:
                        pass

                    #publish date
                    publish_date=''
                    try:
                        publish_date_expression = re.findall(r'"publishDate":{"simpleText":".*?"}', text)
                        publish_date = publish_date_expression[0].replace('"publishDate":{"simpleText":"','')
                        publish_date = publish_date.replace('"}','')
                    except:
                        pass

                    #owner
                    owner=''
                    try:
                        owner_expression =  re.findall(r'"ownerProfileUrl":"http://www.youtube.com/.*?"', text)
                        owner = owner_expression[0].replace('"ownerProfileUrl":"http://www.youtube.com/','')
                        owner = owner.replace('"','')
                    except:
                        pass

                    current_output = {
                        'channel id':ch_id,
                        'channel owner': owner,
                        'Account name': channel_name,
                        'Name of video': title,
                        'views':views,
                        'publish date': publish_date,
                        'video length':video_length,
                        'url':url
                    }
                    
                    new_df = pd.DataFrame(current_output, index=[0])
                    df = pd.concat([df, new_df], ignore_index=True)

                if 'nextPageToken' in response:
                    page_token = response['nextPageToken']
                else:
                    break
                sleep(1)

        except Exception as e:
            log.info(f"Task {self.task_id}: Failed to process the crawling .... Error: {str(e)}")
            self.task_status = TaskStatus.REJECTED.value
            self.url = None

        self.final_output = df

        return self.final_output

if __name__=='__main__':
    task_type = TaskTypes.Youtube.value
    youtube_crawl = Youtube(task_type=task_type)
    youtube_crawl.get_recent_tasks()
    youtube_crawl.process_all_tasks()
