import scrapy
import json
import os
from csv import DictWriter

class Mangatoon(scrapy.Spider):
    name = 'mangatoon'
    file_name='mangatoon.csv' 
    start_urls =[] 
    df_header = {
        "id":[], "title": [], "url": [], "views": [], "likes": [], "tags": [],
        "status": [], "rating": [], "authorName": [], "description":[]
    }
    p=1000000000
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,  # To avoid rate-limiting or server issues
        'DOWNLOAD_DELAY': 3,  # Add delay between requests
        'headers' : {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'MANGATOON_LANGUAGE=en; PHPSESSID=u9g2kucs4gu2d2r580jlg411vg; mangatoon:udid=509c30c5-0791-48d8-a415-942168daf7fa; _gid=GA1.2.1028531497.1709286263; toon_gala_pop_ads=2; _gat_gtag_UA_135467015_1=1; _ga_RYTPVMR6E5=GS1.1.1709291111.2.1.1709291976.0.0.0; _ga=GA1.1.996422051.1709286263',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Origin': 'https://mangatoon.mobi',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
        }
    }
    def __init__(self):
        for i in range(141+1):
            self.start_urls.append(f'https://mangatoon.mobi/en/genre/comic?page={i}')

    def append_list_as_row(self,list_of_elem):
        file_exists = os.path.isfile(self.file_name)
        with open(self.file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def parse(self, response):
        book_links =response.css(".items a::attr(href)").getall()
        for i in range(len(book_links)):
            bl=book_links[i]
            id=bl.split('=')[-1]
            l='https://mangatoon.mobi'+bl
            yield scrapy.Request(url=l,meta={'id':id,'booklink':l},callback=self.parse_book,priority=self.p-i*100)
        self.p-=10000

    def parse_book(self, response):
        meta=response.meta
        title=response.css('.detail-title::text').get()
        status=response.css('.detail-status::text').get()
        views=response.css('.view-count::text').get()
        if views[-1]=='M':
            views=int(float(views[:-1])*1000000)
        elif views[-1]=='k':
            views=int(float(views[:-1])*1000)
        likes=response.css('.like-count::text').get()
        if likes[-1]=='M':
            likes=int(float(likes[:-1])*1000000)
        elif likes[-1]=='k':
            likes=int(float(likes[:-1])*1000)
        rating=response.css('.detail-score-points::text').get()
        authorName=response.css('.detail-author-name span::text').get()
        desc=response.css('.detail-description-all p::text').get()
        tags=response.css('.detail-info a::text').getall()

        data={
            'id':'mangatoon-'+str(meta['id']),
            'title':title,
            'url':meta['booklink'],
            'views':views,
            'likes':likes,
            'tags':tags,
            'status':status,
            'rating':rating,
            'authorName':authorName,
            'description':desc
        }

        self.append_list_as_row(data)


if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(Mangatoon)
    process.start()
