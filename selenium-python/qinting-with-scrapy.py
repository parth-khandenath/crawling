import scrapy
import pandas as pd
import json
import os
from csv import DictWriter

class QingTingSpider(scrapy.Spider):
    name = 'qinting_spider'
    # map = { genrename: [genrecode,lastpage] } 
    map={'sci-fi':['3850',8],'fantasy-romance':['3843',17],'feOriented-mystery':['3844',7],'modern-romance':['3842',155],'ancient-romance':['3841',122],'historical-legends':['3840',38],'fantasy-superPower':['3839',82],'suspense-supernatural':['3838',122],'urban':['3837',160]}
    file_name='' 
    start_urls =[] 
    df_header = {
        "title": [],"id":[], "url": [], "anchors": [], "description": [], "total plays": [],
        "episode count": [], "episode 1 plays": [], "episode 1 date": []
    }
    custom_settings = {
        'CONCURRENT_REQUESTS': 6,  # To avoid rate-limiting or server issues
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
    def __init__(self):
        self.genrename='sci-fi'  #change here
        self.file_name=f'qinting-{self.genrename}'
        for i in range(1,self.map[self.genrename][1]+1):
            print('page:',i)
            self.start_urls.append(f'https://webapi.qingting.fm/api/mobile/categories/521/attr/3289-{self.map[self.genrename][0]}/?page={i}')
    
    def append_list_as_row(self,file_name, list_of_elem):
        file_exists = os.path.isfile(file_name)
        with open(file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def parse(self, response):
        data = json.loads(response.text)
        lst=data.get("FilterList")  
        if lst:
            for entry in lst:
                url1 = f'https://m.qingting.fm/vchannels/{entry["id"]}'
                title = entry['title']
                episodes = entry['program_count']
                descr = entry['description']
                plays = entry['playcount']
                
                url2 = f'https://webapi.qingting.fm/api/mobile/channels/{entry["id"]}'
                url3 = f'{url2}/programs?version='

                yield scrapy.Request(url2, callback=self.parse_channel, meta={'url1': url1, 'title': title,'episodes': episodes, 'descr': descr,'plays': plays, 'url3': url3})
    
    def parse_channel(self, response):
        data = json.loads(response.text)
        anchors = []
        try:
            for anchor in data['channel']['podcasters']:
                anchors.append(anchor['name'])
        except:
            anchors = ['error']

        url3 = response.meta['url3']
        yield scrapy.Request(url3 + str(data['channel']['v']), callback=self.parse_programs,
                             meta={'url1': response.meta['url1'], 'title': response.meta['title'],
                                   'descr': response.meta['descr'], 'plays': response.meta['plays'],
                                   'episodes': response.meta['episodes'], 'anchors': anchors})
    
    def parse_programs(self, response):
        data = json.loads(response.text)
        first_ep_plays = 'error'
        first_ep_date = 'error'

        try:
            first_ep_plays = data['programs'][0]['playCount']
            first_ep_date = data['programs'][0]['updateTime'][:10]
        except:
            pass
        id=(response.meta['url1']).split('/')[-1]
        data= {
            'title': response.meta['title'],
            'id': 'qinting-'+id,
            'url': response.meta['url1'],
            'anchors': response.meta['anchors'],
            'description': response.meta['descr'],
            'total plays': response.meta['plays'],
            'episode count': response.meta['episodes'],
            'episode 1 plays': first_ep_plays,
            'episode 1 date': first_ep_date
        }
        self.append_list_as_row(self.file_name+'.csv',data)

if __name__ == "__main__":
    # df_header = {
    #     "title": [],"id":[], "url": [], "anchors": [], "description": [], "total plays": [],
    #     "episode count": [], "episode 1 plays": [], "episode 1 date": []
    # }
    # file_name='qinting-sci-fi' #change
    # try:
    #     ans = pd.read_csv(f'{file_name}.csv')
    # except:
    #     ans = pd.DataFrame(df_header)
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(QingTingSpider)
    process.start()


# urban - 200:8528 , 404:405
# suspense-supernatural - 200:6452 , 404:229
# fantasy-superPower - 200:4120 , 404:225
# historical-legends - 200:1962 , 404:125
# ancient-romance - 200:6204 , 404:421
# modern-romance - 200:7112 , 404:417
# fantasy-romance - 200:941 , 404:22
# sci-fi - 200:426 , 404:3
# feOriented-mystery - 200:395 , 404:6