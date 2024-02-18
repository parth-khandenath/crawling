import scrapy
import pandas as pd
import json
import os
from csv import DictWriter

class Webtoon(scrapy.Spider):
    name = 'webtoon'
    file_name='kakao-webtoon.csv'  #change
    start_urls =["https://gateway-kw.kakao.com/section/v1/timetables/days?placement=timetable_completed"] 
    df_header = {
        "title": [], "id":[], "adult":[], "url": [], "views":[], "genre":[], "likes": [], "author": [], "publisher": [],
        "summary": [], "keywords/tags": [], "related novels": []
    }
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,  # To avoid rate-limiting or server issues
        'DOWNLOAD_DELAY': 1,  # Add delay between requests
        'headers' : {
            'Authority': 'gateway-kw.kakao.com',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ko',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Cookie': '_kpdid=09c1e5784fc6478994c04ff04c092e5b; _kpiid=bb367fa490bc82b7fd585f1b1b782703; _kadu=8BVOmyKYYpjOcGXQ_1704343293676; theme=dark; _kp_collector=KP.3310808493.1707890282561; _gcl_au=1.1.567674066.1707890283; _gid=GA1.2.198880558.1707890284; _fbp=fb.1.1707890284840.685466663; _ga=GA1.2.1891870976.1707890284; _ga_GLWD7GS60Q=GS1.2.1707907879.3.1.1707909529.49.0.0; _T_ANO=Dhh1nrVNwb0KOIOyvRll5gfKhLngRXFwsN80wnBqyvtfkwNufwFnnkgJj0O7O2cAB93wve7Rwvz+ZS8Eo7sEPLkTQn6AEPnoBxI/6xjPq+J8E82c881MeAFUmZNK9tfNiAcLh2xf0FPVXdyu5ZCoXxCyRd7qoEFS8CXEW8F/wAFuKYB6NOKCfTboKLn59MGDnuzYWcuPaiccEcjxEPs/Pt3lKe4+IPvL+8/EUMSG0moCNRF1vONe5hafCzWoSiZnpfpbB8ot1HRAvOkUGeuaDBb0pVNkmfWb+baVBWz8mOCDRoRF1oghcKB5OVC/bOe9zOqRwyncVBb822RALwWgZg==; _ga_80D69HE0QD=GS1.1.1707907879.3.1.1707910306.0.0.0',
            'Origin': 'https://webtoon.kakao.com',
            'Referer': 'https://webtoon.kakao.com/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'Sec-ch-ua-mobile': '?0',
            'Sec-ch-ua-platform': '"Windows"'
        }
    }

    
    def append_list_as_row(self,file_name, list_of_elem):
        file_exists = os.path.isfile(file_name)
        with open(file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def parse(self, response):
        res_json = json.loads(response.text)  #1500
        p=1000000
        count=0
        for obj in res_json['data'][0]['cardGroups'][0]['cards']:
            count+=1
            # if count==20:
            #     break
            title=obj['content']['seoId']
            book_id=str(obj['content']['id'])
            adult=obj['content']['adult']
            book_url=f'https://webtoon.kakao.com/content/{title}/{book_id}'
            author=[]
            publisher=[]
            for objj in obj['content']['authors']:
                if objj['type']=="AUTHOR":
                    author.append(objj['name'])
                elif objj['type']=='PUBLISHER':
                    publisher.append(objj['name'])
            tags=obj['content']['seoKeywords']

            meta={
                'title':title,
                'book_id':book_id,
                'adult': adult,
                'book_url': book_url,
                'author': author,
                'publisher': publisher,
                'tags': tags,
                'p':p-count*100
            }

            yield scrapy.Request(book_url, callback=self.parse_book, meta=meta, priority=p-count*100)
    
    def parse_book(self, response):
        meta=response.meta
        if meta['adult']:
            genre="NA"
            views="NA"
            likes="NA"
        else:
            info=response.css('.ml-2::text').getall()
            genre=info[0]
            views=info[1]
            likes=info[2]

        meta['views']=views
        meta['genre']=genre
        meta['likes']=likes
        meta['p']=meta['p']-10

        url=f'https://gateway-kw.kakao.com/decorator/v2/decorator/contents/{meta['book_id']}/profile'
        yield scrapy.Request(url, callback=self.get_more, meta=meta,priority=meta['p'])
    
    def get_more(self, response):
        meta=response.meta
        res_json = json.loads(response.text)
        meta['title']=res_json['data']['title']
        summary=res_json['data']['synopsis']
        print("##################")
        print(meta['adult'])
        print("##################")
        rcmnds=[]
        rclst=[]
        if res_json['data']['recommendations']:
            rclst=res_json['data']['recommendations'][0]['contents']
        for r in rclst:
            rcmnds.append({
                'id': r['id'],
                'title': r['title'],
                'url': f"https://webtoon.kakao.com/content/{r['seoId']}/{r['id']}"
            })
        
        data= {
                 'title':meta['title'], 
                 'id':'kakaowebtoon-'+meta['book_id'], 
                 'adult':meta['adult'], 
                 'url':meta['book_url'], 
                 'views':meta['views'], 
                 'genre':meta['genre'], 
                 'likes':meta['likes'], 
                 'author':meta['author'], 
                 'publisher':meta['publisher'], 
                 'summary':summary, 
                 'keywords/tags':meta['tags'], 
                 'related novels':rcmnds
        }
        self.append_list_as_row(self.file_name,data)

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(Webtoon)
    process.start()