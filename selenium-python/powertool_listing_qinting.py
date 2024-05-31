import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess
import json
import os
from csv import DictWriter

class PowertoolListingQingtingSpider(scrapy.Spider):
    name = 'listing_Qinting'
    map={'sci-fi':['3850',8],'fantasy-romance':['3843',17],'feOriented-mystery':['3844',7],'modern-romance':['3842',155],'ancient-romance':['3841',122],'historical-legends':['3840',38],'fantasy-superPower':['3839',82],'suspense-supernatural':['3838',122],'urban':['3837',160]}
    file_name='' 
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

    def __init__(self, **kwargs):
            self.genrename = kwargs['genre']
            self.output_dict = kwargs['output_dict']
            self.file_name=f'qinting-{self.genrename}'
            self.data_list = []

    def start_requests(self):
        for i in range(1,self.map[self.genrename][1]+1):
            print('page:',i)
            yield scrapy.Request(url =f'https://webapi.qingting.fm/api/mobile/categories/521/attr/3289-{self.map[self.genrename][0]}/?page={i}')
            return

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
                if plays[-1] == "万":
                    plays = float(plays[:-1]) * 10000
                    plays = int(plays)

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
            if first_ep_plays[-1] == "万":
                first_ep_plays = float(first_ep_plays[:-1]) * 10000
                first_ep_plays = int(first_ep_plays)
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
        self.data_list.append(data)

    def closed(self, reason):
        df = pd.DataFrame(self.data_list)
        self.output_dict[self.file_name]=df

def main(output_dict):
    genres = ['sci-fi', 'fantasy-romance', 'feOriented-mystery', 'modern-romance', 'ancient-romance','historical-legends','fantasy-superPower','suspense-supernatural','urban']
    process = CrawlerProcess()

    def next_crawl(i):
        try:
            a = process.crawl(PowertoolListingQingtingSpider, genre=genres[i], output_dict=output_dict)
            a.addCallback(lambda _: next_crawl(i + 1))
        
        except IndexError:
            # process.stop()
            pass

    next_crawl(0)
    process.start()
    import sys
    del sys.modules['twisted.internet.reactor']
    from twisted.internet import reactor
    from twisted.internet import default
    default.install()

if __name__ == "__main__":
    output_dict = {'output':None}
    main(output_dict)
    print(output_dict)

# urban - 200:8528 , 404:405
# suspense-supernatural - 200:6452 , 404:229
# fantasy-superPower - 200:4120 , 404:225
# historical-legends - 200:1962 , 404:125
# ancient-romance - 200:6204 , 404:421
# modern-romance - 200:7112 , 404:417
# fantasy-romance - 200:941 , 404:22
# sci-fi - 200:426 , 404:3
# feOriented-mystery - 200:395 , 404:6
