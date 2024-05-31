import scrapy
import pandas as pd
import re

def process(num):
    if not num or len(str(num))==0:
        return 'NA'
    num=str(num)
    if num[-1]=='M':
        num=int(float(num[:-1])*1000000)
    elif num[-1]=='K':
        num=int(float(num[:-1])*1000)
    else:
        num=int(num)
    return num

class inkr(scrapy.Spider):
    name = 'inkr' 
    allowed_domains = ['https://comics.inkr.com','comics.inkr.com']
    start_urls = []
    books=0

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'Origin':'https://comics.inkr.com',
        'Referer': 'https://comics.inkr.com/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        # 'Cookie':'GUID=a03ebd3f-9d62-4062-a757-f6123b8d0828; __root_domain_v=.4yt.net; _qddaz=QD.165103683998284; Hm_lvt_9ebbc52cb334f47110052681488d16f0=1703657826,1703683996,1704221291; acw_sc__v2=65945b12b82909c1927ec78e18bf061b4739eac4; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22a03ebd3f-9d62-4062-a757-f6123b8d0828%22%2C%22%24device_id%22%3A%2218ca9eb71192ab-06856b14af844c-26001951-1327104-18ca9eb711a77%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24latest_referrer_host%22%3A%22www.google.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%7D; _qdda=3-1.10ga5x; _qddab=3-2t77f8.lqwpo5fj; lastSE=google; acw_tc=2760828817042231544621051e4ed94ba624b232f5d6c5f3d24565c81b79a8; acw_sc__v2=659461cab8540a0243f392032c1871b888431069; Hm_lpvt_9ebbc52cb334f47110052681488d16f0=1704223181; ssxmod_itna2=mq0x0D2DRi0=0QG8DzxAx=r=TaEzY5dWYYqD61bQD0vyq03qD9DHa08Dwjy0RLTTU1ZK4APzrIgqojGui0fEUY=I1myq43m4e93j0jK/0wU08+ARrP98cn7kh0whB3lYPwwz2UM2Q8G1YBYx6MQwfgi1Q+GxNb2LBo2+fD=qpCbMlwpxQYNcBhGtBfrvGo+x+RAYRqnc8j=dqrf38DISUd45yMiwmD6SYnAdiMFsa7RS78T+geEl/aXAgOtXtW=ChrhxBfBjkOIGCWAq9KnL+YAfZOdVBQ+S7vPkyxWsG80+zAtglx7emdFlDgQdsmQO0EijqVcoWaok0odc0SWmfEi+YmGWm9eesjrj13=RvzjKKa=Tbbeeh0AIuB2HRoKc0ZndInInCpTf5=Zjz86TaGylTFtu1DLsRjG2TnGte1NEGuY1mp2I+7nr8u006AU05nG9AGKnD4OomCj37Gs0A5AwF0d4zWS1bpj=uYAsgAFADKOPdK6O7iH0Yu1A8ldxs7/4rAoTb/h+bmYC4DQFDoGBFMtziy0p4DpFRCo9Cvo7zbFd8MI5c9Sl4QDHD2fvALgQDFqD+ODxD===; ssxmod_itna=QuDQYKiKBI8Hi=DXDnCmvK=pYGCtDjh8DqqGXwoGRDCqAPGwDebSpAi3EYxfDDvPvlabcGiv/=SWYqvFBj0ECVmDB3DEc8i4oaxeeDv+xGoDPxDeDADYEFDAkPD9D048y2pLKGWDbx=DaxDbDie82DGCDeKD0xD87x07DQy8PDDzPAoisxrYVrYFYUbmX=Dh5CD8D7ymDlPeUFD8Q/8jP75hvI8sveqDXZdDvoy3ycbmDBR8B=HsSi2ooihegmiaimRD5lw5WW0rWdRNmWDezebaqD2DzAnrM7btHWGDD===',
    }

    def __init__(self, **kwargs):
        self.output_dict = {}
        self.books=0
        self.priority = 1000000
        self.output = []
        genres=['action','romance','bl','adventure','comedy','fantasy','horror','gl']
        for genre in genres:
            self.start_urls.append(f'https://comics.inkr.com/{genre}/list/all')

    def parse(self, response):
        links=response.css('.f5qjf .__8K_Wq::attr(href)').getall()
        n=len(links)
        links=links[:n//2]
        # print(links)
        for l in links:
            id=l.split('?')[0].split('/')[-1]
            yield scrapy.Request(l,callback=self.parse_book,meta={'id':id,'book_link':l})

    def parse_book(self, response):
        meta=response.meta

        title = response.css('h1.z_0JS::text').get()
        stats = response.css('.ybKZZ :not(.e1MzF)::text').getall()
        # print(stats)
        reads=stats[0]
        reads=process(reads)
        likes=stats[1]
        likes=process(likes)
        genres=response.css('.aWlw4.typography-16-normal .__8K_Wq::text').getall()[1:]
        tags=response.css('.nV_Ja::text').getall()
        # lastchapter=response.css('div.NaFHI::text').get()
        summary=response.css('div.EZ5g3::text').get()
        # summary=response.xpath('normalize-space(string(//div[@class="EZ5g3"]))').get()
        c_eles=response.css('.ZK2OT')  #.getall()
        n=len(c_eles)
        c_eles=c_eles[:n//2]
        credits=[]
        for ele in c_eles:
            name=ele.css('a span::text').get()
            role=''
            for r in ele.css('.__4lRSY div::text').getall(): 
                role+=r
            credits.append(name+':'+role)
        l=meta['book_link']
        data = {
            'id':'inkr-'+meta['id'],
            'url':l,
            'title':title,
            'reads':reads,
            'likes':likes,
            'genres':genres,
            'tags':tags,
            # 'lastchapter':lastchapter,
            'summary':summary,
            'credits':credits
        }
        chapt_link=l.split('?')[0]+'/chapters'
        yield scrapy.Request(chapt_link,callback=self.parse_chpt,meta=data)

    def parse_chpt(self, response):
        meta=response.meta
        toalchpts=response.css('div.__9zCyV::text').get()
        meta['total_chapts']=toalchpts
        self.output.append(meta)
        self.books+=1
        print(self.books)
        df = pd.DataFrame(self.output)
        df.to_csv('inkr.csv', index=False)

    def closed(self, reason):
        df = pd.DataFrame(self.output)
        df.to_csv('inkr.csv', index=False)