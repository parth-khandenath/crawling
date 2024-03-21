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
        'Cookie': 'HWWAFSESID=b7e7a737be5a8cb9e0; HWWAFSESTIME=1703073273454; INGRESSCOOKIE=1703073274.461.3351.108366; HWWAFSESID=40bf57f1284c17d700; HWWAFSESTIME=1703047235393',
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

    def parse(self, response):
        links=[]
        url = "https://pbaccess.wetv.vip/trpc.video_app_international.trpc_filter_page.FilterPage/GetFilterPage?vappid=92089330&vsecret=cd21b1cef4d2ac7d600e5d3e4f1b1fb612a31b4c6ccf5c8d&video_appid=1200004&ver=1"
        headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'content-type': 'application/json',
        'cookie': 'country_code=153512; lang_code=1491988; guid=d368a95b07fb1aa31cce5a3403911d13; video_guid=d368a95b07fb1aa31cce5a3403911d13; uin=d368a95b07fb1aa31cce5a3403911d13; wetv_lang=en; wetv_pt=v; video_appid=1200004; _gcl_au=1.1.1930857218.1710911963; _gid=GA1.2.1850274373.1710911963; _fbp=fb.1.1710911963764.495723053; __lt__cid=f093ca5d-8b18-4587-b005-e27519fb5086; __lt__sid=009d080c-93d12637; vplatform=2; _qimei_uuid42=18314170f071008fca6ac84ecb10364e9e50fc66c5; h38=18314170f071008fca6ac84ecb10364e9e50fc66c5; _qimei_fingerprint=1c609ff4531c6a835b185cfa96d323f7; _qimei_q36=; _qimei_h38=2db8b40fca6ac84ecb10364e02000009e18315; __gads=ID=44bf91fa5f199e21:T=1710956973:RT=1710959606:S=ALNI_MaP933UU3QJlZ8ceg1JyG-LxsCpwQ; __gpi=UID=00000d4c28adaa82:T=1710956973:RT=1710959606:S=ALNI_MZAInFZ6D-DBhxw4QyvShZq8IZGrg; __eoi=ID=ef7297e369adbe42:T=1710956973:RT=1710959606:S=AA-AfjbdFgXKzZ6trKXAFt95FwAb; FCNEC=%5B%5B%22AKsRol9MU4nsKp-gamuXEjkc_xgPnmiqGTQhwUUvWlt9As1Wr3nfCE6yAnuHf-v8-4AgsC5-BG6YsDvuTjDffiLEcsbkSl4HVbUE_2x2JWCYWiA3BWXx1x6iR18TDLCo79Crc8nXfgyVEQiVNk6Ro01IzDzutZrt9Q%3D%3D%22%5D%5D; _ga=GA1.1.232802559.1710911963; _ga_LMMR6KN931=GS1.2.1710952329.3.1.1710960385.60.0.0; _ga_2VG0PSP9MN=GS1.2.1710952329.3.1.1710960386.60.0.0; _ga_ZZRPPC4YSC=GS1.1.1710952323.4.1.1710960387.57.0.0; _ga_YRZXWWKXN0=GS1.1.1710952328.4.1.1710960387.0.0.0; _ga_5NSWYK5E9J=GS1.1.1710952326.4.1.1710960387.57.0.0; h38_sign=000000014068b89153f4562362f80aafc61c5f2a1f1bbe9f47f26dad070abd01ceba28659bb6a5b7a8a1a9fd5e612dcfa466e132715d14da51274d5783ca9b054eb4904d071ce00c3190193d6ee2a583520b50f609b9fd4b0ec83d6db51719869479e9b9660e3fcc1bdb349be281c164027392baf0de1f0a05059ddc41a77719f15ed9180d5e611ea61b4a258d7fd75cccf99765f4c3adeccc094b5b92ef16aa86bd61d95d65385577c48ea7340981c67fabd495f14541bdedaf04842e0cb8dca8c73c2ca36ee1aa340a094f33184bcfe2a2c731a88a2883258a010276',
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

