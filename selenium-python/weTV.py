import scrapy
from scrapy.crawler import CrawlerProcess
import requests
import json
import time
import os
from csv import DictWriter

class weTvspider(scrapy.Spider):
    name = 'we_tv_spider'
    file_name='' 
    start_urls =[] 
    df_header= {"bookId":[], "title": [],"bookUrl": [], "genre": [], "region": [], "bookCreateTime": [], "chaptersTotal": [], "introduction": []}

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,  # To avoid rate-limiting or server issues
        # 'DOWNLOAD_DELAY': 3,  # Add delay between requests
        'headers' : {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"'
        }
    }
    def __init__(self, link, name):
        self.start_urls.append(link)
        self.file_name=name+'.csv'
        self.cat_id=(link.split('first_category=')[1]).split('&')[0]

    def append_list_as_row(self, list_of_elem):
        file_exists = os.path.isfile(self.file_name)
        with open(self.file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def construct_cookie_string(self, dict):
        s = ""
        for k, v in dict.items():
            s += f"{k}={v}; "
        return s

    def parse(self, response):

        cookies = {}
        for header in response.headers.getlist("Set-Cookie"):
            cookie = header.decode("utf-8")
            key_value = cookie.split(";")[0]
            key, value = key_value.split("=")
            cookies[key.strip()] = value.strip()
        cookies = self.construct_cookie_string(cookies)

        links=[]
        url = "https://pbaccess.wetv.vip/trpc.video_app_international.trpc_filter_page.FilterPage/GetFilterPage?vappid=92089330&vsecret=cd21b1cef4d2ac7d600e5d3e4f1b1fb612a31b4c6ccf5c8d&video_appid=1200004&ver=1"
        headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'cookie': cookies,
        'origin': 'https://wetv.vip',
        'referer': 'https://wetv.vip/en/channel/10262?id=10262&first_category=3&type=PAGE_TYPE_ALBUM_FILTER',
        'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36'
        }

        baseurl='https://wetv.vip/en/play/'
        pagesdone=0
        while True:
            time.sleep(1.5)
            print('pagesdone: ',pagesdone)
            payload = json.dumps({
                "user_choice": {
                    "first_category": self.cat_id,
                    "main_genre_id,sub_genre_id": "0",
                    "sort": "2",
                    "pay_status": "0"
                },
                "page_ctx": f"from={pagesdone}&size=30"
                })
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code!=200:
                break
            res_json=response.json()
            posters=res_json["data"]["data"]["posters"]
            if posters==[]:
                break
            for poster in posters:
                links.append(baseurl+poster["cid"])
            pagesdone+=30
        for l in links:
            yield scrapy.Request(url=l, callback=self.parse_book)

    def parse_book(self, response):
        print(response.url)
        countries=["Mainland, China","Mainland,China","South Korea","Japan","Indonesia","Thailand"]

        id=(response.url.split('-')[0]).split('/')[-1]
        title=response.css("h1.title--main::text").get()
        bookUrl=f"https://wetv.vip/en/play/{id}"
        stats=response.css(".play-info__text span::text").getall()
        genres=[]
        chaps="NA"
        region="NA"
        releaseyear="NA"
        for stat in stats:
            if stat.strip().isdigit():
                releaseyear=stat
            elif "All" in stat or "EPs" in stat:
                chaps=stat[4:-4]
            elif stat in countries:
                region=stat
            elif stat!='|' and stat.strip() != '':
                if ' · ' in stat:
                    genres=stat.split(' · ')
                else:
                    genres=[stat]
        intro=response.css('.play-desc.play-collapse.play-desc--show::text').get()

        data = {"bookId":"weTV-"+id, "title": title,"bookUrl": bookUrl, "genre": genres, "region": region, "bookCreateTime": releaseyear, "chaptersTotal": chaps, "introduction": intro}
        
        self.append_list_as_row(data)

def main():
    links=[
        "https://wetv.vip/en/channel/10259?id=10259&first_category=2&type=PAGE_TYPE_ALBUM_FILTER",
        "https://wetv.vip/en/channel/10262?id=10262&first_category=3&type=PAGE_TYPE_ALBUM_FILTER"]
    names=[
        "weTV-TV Drama", 
        "weTV-Anime"]
    process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'})

    def next_crawl(i):
        try:
            # if i>28:
            a = process.crawl(weTvspider, link=links[i], name=names[i])
            a.addCallback(lambda _: next_crawl(i + 1))
            # else:
            #     next_crawl(i+1)
        except IndexError:
            # process.stop()
            pass

    next_crawl(0)
    process.start()

if __name__ == "__main__":
    main()

