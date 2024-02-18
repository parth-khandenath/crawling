import scrapy
import pandas as pd
import json
import os
from csv import DictWriter

class Fanqie(scrapy.Spider):
    name = 'fanqie'
    gender='female'   #change
    file_name=f'fanqie-{gender}.csv'  
    start_urls =[] 
    df_header = {
        "title": [],"id":[], "url": [], "word_count": [], "read_count": [], "chapter_count": [],
        "author": [], "tags": [], "synopsis": [], "1st chapter date": []
    }
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,  # To avoid rate-limiting or server issues
        'DOWNLOAD_DELAY': 1,  # Add delay between requests
        # 'headers' : {
        # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        # 'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        # 'Cache-Control': 'max-age=0',
        # 'Connection': 'keep-alive',
        # 'Cookie': 'HWWAFSESID=b7e7a737be5a8cb9e0; HWWAFSESTIME=1703073273454; INGRESSCOOKIE=1703073274.461.3351.108366; HWWAFSESID=40bf57f1284c17d700; HWWAFSESTIME=1703047235393',
        # 'Sec-Fetch-Dest': 'document',
        # 'Sec-Fetch-Mode': 'navigate',
        # 'Sec-Fetch-Site': 'none',
        # 'Sec-Fetch-User': '?1',
        # 'Upgrade-Insecure-Requests': '1',
        # 'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        # 'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        # 'sec-ch-ua-mobile': '?1',
        # 'sec-ch-ua-platform': '"Android"'
        # }
    }
    def __init__(self):
        if self.gender=="male":
            gendercode=1
        else:
            gendercode=0
        for pgindx in range(99):
            url = f"https://fanqienovel.com/api/author/library/book_list/v0/?page_count=18&page_index={pgindx}&gender={gendercode}&category_id=-1&creation_status=-1&word_count=-1&book_type=-1&sort=0&msToken=wmFNB1WglSURL2ZxtGCZKsZ6VPXCYgSWCvwqkDL9PQAHFk_l9ZMcDH9WuL9Y9moMkawtnc0kA04YxFfW8hE7sepYSfM3WvwPEAujfO3XXKZav0ZLRtjFB62YFpcp9w%3D%3D&a_bogus=mXsxgcgjMsm1XEVDywkz9JXm4Jb0YWRUgZEzRKuB5ULF"
            self.start_urls.append(url)
    
    def append_list_as_row(self,file_name, list_of_elem):
        file_exists = os.path.isfile(file_name)
        with open(file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def parse(self, response):
        res_json = json.loads(response.text)
        for book in res_json['data']['book_list']:
            book_id=str(book['book_id'])
            book_url=f'https://fanqienovel.com/page/{book_id}'
            meta={
                # 'abstract':book['abstract'],
                # 'author':book['author'],
                # 'book_name':book['book_name'],
                # 'word_count':book['word_count'],
                # 'read_count':book['read_count'],
                'book_id': book_id,
                'url': book_url
            }

            yield scrapy.Request(book_url, callback=self.parse_book, meta=meta)

    def parse_book(self,response):  #some books have empty webpages starting from page 7 (male)
        meta=response.meta
        book_name=response.css(".info-name h1::text").get()
        abstract=response.css(".page-abstract-content p::text").get()
        author=response.css(".author-name-text::text").get()
        word_count1=response.css(".info-count-word .detail::text").get()
        word_count2=response.css(".info-count-word .text::text").get()
        if word_count1 and word_count2:
            wc=word_count1+word_count2
            wc=wc[:-1]
        else:
            wc=None
        read_count1=response.css(".info-count-read .detail::text").get()
        read_count2=response.css(".info-count-read .text::text").get()
        if read_count1 and read_count2:
            rc=read_count1+read_count2
            rc=rc.split('人')[0]
        else:
            rc=None
        tags=response.css(".info-label-grey::text").getall()        
        total_chapters=response.css(".page-directory-header h3::text").get()   
        all_chps=response.css("a.chapter-item-title::attr(href)").getall()
        if all_chps:
            chp1_link= 'https://fanqienovel.com'+all_chps[1]
        else:
            chp1_link=None
        meta['tags']=tags
        meta['total_chapters']=total_chapters
        meta['word_count']=wc
        meta['read_count']=rc
        meta['abstract']=abstract
        meta['author']=author
        meta['book_name']=book_name

        if chp1_link:
            yield scrapy.Request(chp1_link, callback=self.parse_chp, meta=meta)

    def parse_chp(self,response):
        meta=response.meta
        chpt1_date=response.css(".desc-item+ .desc-item::text").get()
        data={
            "title": meta['book_name'],"id":'fanqie-'+meta['book_id'], "url": meta['url'], "word_count": meta['word_count'], "read_count": meta['read_count'], "chapter_count": meta['total_chapters'], "author": meta['author'], "tags": meta['tags'], "synopsis": meta['abstract'], "1st chapter date": chpt1_date
        }
        self.append_list_as_row(self.file_name,data)
    
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(Fanqie)
    process.start()

# import requests

# gender="male"
# file_name="fanqie-male.csv"

# headers = {
#   'authority': 'fanqienovel.com',
#   'accept': 'application/json, text/plain, */*',
#   'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
#   'cookie': 'Hm_lvt_2667d29c8e792e6fa9182c20a3013175=1707930749; csrf_session_id=4bb4d36d169ccbee78562dc9aa700a4f; novel_web_id=7335506627992815138; s_v_web_id=verify_lsm1vg0o_PscrwGMV_EDGb_4aLN_8vNm_8bqEPlvo84EP; msToken=H-dTjKxJaEhiNCxWYyxRhuTeICqFjUZIZCXHBKEI-RoHHNL0jSGBtUWYqV_Y-p1atz4TGQ0y2u-os-sXzZ5SZ1UEbGxyCTTt3AmyUfdSnRCx6noSeKs_CY2uhA_LYA==; Hm_lpvt_2667d29c8e792e6fa9182c20a3013175=1707932201; ttwid=1%7CWClykbAhK-iYo-2zmlHV860I2Z1aVJG1ZAMC4wHI6yU%7C1707932201%7C59a775ce992e322a1a62cc683e9256ab8fa6d21f6f0a28050885c70c56c28abb; msToken=gOAw7uOyC0RNM46QZFm0lEJwwFctQVcrpsfhoFySXhqEPWjSKTO_3CtZxZffEMCTuyZzdxixLbSn8YF0qldY7lKdRlN6Votc8j7nqUbjFWjikbcqEdDhaaDh5K-_VQ==',
#   'referer': 'https://fanqienovel.com/library/audience1/page_3?sort=hottes',
#   'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
#   'sec-ch-ua-mobile': '?0',
#   'sec-ch-ua-platform': '"Windows"',
#   'sec-fetch-dest': 'empty',
#   'sec-fetch-mode': 'cors',
#   'sec-fetch-site': 'same-origin',
#   'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
# }

# pgindx=1
# while pgindx <= 99:
#     
#     url = f"https://fanqienovel.com/api/author/library/book_list/v0/?page_count=18&page_index={pgindx}&gender={gendercode}&category_id=-1&creation_status=-1&word_count=-1&book_type=-1&sort=0&msToken=wmFNB1WglSURL2ZxtGCZKsZ6VPXCYgSWCvwqkDL9PQAHFk_l9ZMcDH9WuL9Y9moMkawtnc0kA04YxFfW8hE7sepYSfM3WvwPEAujfO3XXKZav0ZLRtjFB62YFpcp9w%3D%3D&a_bogus=mXsxgcgjMsm1XEVDywkz9JXm4Jb0YWRUgZEzRKuB5ULF"
#     response = requests.request("GET", url, headers=headers)
#     res_json = response.json()




#     pgindx+=1