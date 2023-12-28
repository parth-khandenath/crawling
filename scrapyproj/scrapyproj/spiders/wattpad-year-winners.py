import scrapy
import pandas as pd
import json
import requests

class QuoteSpider(scrapy.Spider):
    name = 'wattpad22'
    start_urls = ['https://www.wattpad.com/list/'] 
    custom_settings={
        'CONCURRENT_REQUESTS':1
    }
    year='featured' #put year here #when you want novels from https://www.wattpad.com/featured/703389905 put the year as 'featured' (wattpad studio hits)
    file_name=f'wattpad-{year}-winners' 
    sheet = 'wattpad_listing'
    Headers = {"title":[] , "book_url":[], "read_count":[] , "vote_count":[], "parts":[], "time (hrs.)":[], "author":[], "status":[], "mature_status":[], "description":[], "tags":[], "chapter1_publish_date":[],"book_id":[]}
    ans = pd.DataFrame(Headers)
    p=1000000

    def parse(self,response):
        offset=0
        limit=100
        map={2020:'996419659',2021:'1192808633',2022:'1354128786',2023:'1509052297','featured':'703389905'} #put the corresponding number for that year in the map
        url = f"https://www.wattpad.com/api/v3/lists/{map[self.year]}/stories?fields=stories%28id%2Ctags%2Ctitle%2Ccover%2Cdescription%2Curl%2Clength%2CvoteCount%2CreadCount%2CcommentCount%2CnumParts%2Ccompleted%2Cmature%2Cuser%28name%2Cavatar%29%2CfirstPublishedPart%28createDate%29%29%2Ctotal%2CnextUrl&offset={offset}&limit={limit}" 

        payload = {}
        headers = {
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'Authorization': 'IwKhVmNM7VXhnsVb0BabhS',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Referer': 'https://www.wattpad.com/',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua-platform': '"Linux"',
        'Cookie': 'lang=1; locale=en_US'
        }

        books_response = requests.request("GET", url, headers=headers, data=payload)


        if books_response.status_code==200:
                response_json=books_response.json()
                books_list=response_json['stories']
                for book in books_list:
                    book_id=book['id']
                    title=book['title']
                    book_url=book['url']
                    book_reads=book['readCount']
                    totalVotes=book['voteCount']
                    num_parts=book['numParts']
                    time=book['length']/69000
                    time=float("{:.2f}".format(time))   
                    author=book['user']['name']
                    status="ongoing"
                    if book['completed']==True:
                        status='completed'
                    mature_status=book['mature']
                    description=book['description']
                    tags=book['tags']
                    chapter1_publish_date=book['firstPublishedPart']['createDate'][:10]
                    self.ans.loc[len(self.ans.index)] = [title,book_url,book_reads,totalVotes,num_parts,time,author,status,mature_status,description,tags,chapter1_publish_date,book_id]
        else:
                print("Could not fetch books...")
                print(f"Status code:{books_response.status_code}") 

    def closed(self,reason):
        self.ans.to_csv(f'{self.file_name}.csv',index=False)