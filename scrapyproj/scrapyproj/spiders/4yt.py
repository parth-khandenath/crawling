import scrapy
import pandas as pd
import re

def find_right_date(type,start_ind,chapter_times):
    m=1
    if type=="last":
        m=-1
    right_date=chapter_times[start_ind][-19:-9]
    next=1  #checking for a valid start date
    while not check(right_date) and next<=10 and start_ind+m*next<len(chapter_times) and start_ind+m*next>0:
        right_date=chapter_times[start_ind+m*next][-19:9]
        next+=1
    if not check(right_date):
        return "N/A"
    return right_date

def check(date):
    date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
    # valid_chars=['0','1','2','3','4','5','6','7','8','9','-']
    dates = re.findall(date_pattern, date)
    return len(dates)==1

class Spider4ytSpider(scrapy.Spider):
    name = 'spider_4yt' 
    allowed_domains = ['www.4yt.net']
    start_urls = ['https://www.4yt.net/all/book/0_0_0_0_0_4.html?keyword=&fuzzySearchType=1&page=' +
                  str(i) for i in range(1, 13)]

    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'Origin':'https://www.4yt.net',
        'Referer': 'https://www.4yt.net/',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        # 'Cookie':'GUID=a03ebd3f-9d62-4062-a757-f6123b8d0828; __root_domain_v=.4yt.net; _qddaz=QD.165103683998284; Hm_lvt_9ebbc52cb334f47110052681488d16f0=1703657826,1703683996,1704221291; acw_sc__v2=65945b12b82909c1927ec78e18bf061b4739eac4; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22a03ebd3f-9d62-4062-a757-f6123b8d0828%22%2C%22%24device_id%22%3A%2218ca9eb71192ab-06856b14af844c-26001951-1327104-18ca9eb711a77%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24latest_referrer_host%22%3A%22www.google.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%7D; _qdda=3-1.10ga5x; _qddab=3-2t77f8.lqwpo5fj; lastSE=google; acw_tc=2760828817042231544621051e4ed94ba624b232f5d6c5f3d24565c81b79a8; acw_sc__v2=659461cab8540a0243f392032c1871b888431069; Hm_lpvt_9ebbc52cb334f47110052681488d16f0=1704223181; ssxmod_itna2=mq0x0D2DRi0=0QG8DzxAx=r=TaEzY5dWYYqD61bQD0vyq03qD9DHa08Dwjy0RLTTU1ZK4APzrIgqojGui0fEUY=I1myq43m4e93j0jK/0wU08+ARrP98cn7kh0whB3lYPwwz2UM2Q8G1YBYx6MQwfgi1Q+GxNb2LBo2+fD=qpCbMlwpxQYNcBhGtBfrvGo+x+RAYRqnc8j=dqrf38DISUd45yMiwmD6SYnAdiMFsa7RS78T+geEl/aXAgOtXtW=ChrhxBfBjkOIGCWAq9KnL+YAfZOdVBQ+S7vPkyxWsG80+zAtglx7emdFlDgQdsmQO0EijqVcoWaok0odc0SWmfEi+YmGWm9eesjrj13=RvzjKKa=Tbbeeh0AIuB2HRoKc0ZndInInCpTf5=Zjz86TaGylTFtu1DLsRjG2TnGte1NEGuY1mp2I+7nr8u006AU05nG9AGKnD4OomCj37Gs0A5AwF0d4zWS1bpj=uYAsgAFADKOPdK6O7iH0Yu1A8ldxs7/4rAoTb/h+bmYC4DQFDoGBFMtziy0p4DpFRCo9Cvo7zbFd8MI5c9Sl4QDHD2fvALgQDFqD+ODxD===; ssxmod_itna=QuDQYKiKBI8Hi=DXDnCmvK=pYGCtDjh8DqqGXwoGRDCqAPGwDebSpAi3EYxfDDvPvlabcGiv/=SWYqvFBj0ECVmDB3DEc8i4oaxeeDv+xGoDPxDeDADYEFDAkPD9D048y2pLKGWDbx=DaxDbDie82DGCDeKD0xD87x07DQy8PDDzPAoisxrYVrYFYUbmX=Dh5CD8D7ymDlPeUFD8Q/8jP75hvI8sveqDXZdDvoy3ycbmDBR8B=HsSi2ooihegmiaimRD5lw5WW0rWdRNmWDezebaqD2DzAnrM7btHWGDD===',
    }

    def __init__(self, **kwargs):
        self.output_dict = {}
        self.priority = 1000000
        self.output = []

    def parse(self, response):
        base_url = 'https://www.4yt.net'
        urls = response.css('.bookName a::attr("href")').getall()
        print("########")
        print(urls)

        for url in urls:
            if 'www' in url:
                yield response.follow(url=url, callback=self.parse_book)
            else:
                if url[0]!='/':
                    url='/'+url
                yield response.follow(url=base_url+url, callback=self.parse_book)

    def parse_book(self, response):
        book_link = response.url

        title = response.css('div.book-head div.cont span.h1::text').get()
        author = response.css('div.book-head div.cont span.h2::text').get()
        status=response.css('a.blue::text').get()
        if status=='完本小说':
            status='completed'
        elif status=='连载中':
            status='ongoing'

        chapter_times= response.css('.volume dd a::attr("title")').getall()
        approx_num_chapts=len(chapter_times) 
        #finding approx novel start time
        # approx_novel_start=chapter_times[0][-19:-9]
        start=0
        if len(chapter_times)>12:  #recommendation section (to be skipped)
            # approx_novel_start=chapter_times[12][-19:-9] 
            start=12 #skipped 12 links (assuming recommendation)
        approx_novel_start=find_right_date("start",start,chapter_times)
        last_chapter_time=find_right_date("last",approx_num_chapts-1,chapter_times)

        tags = response.css('div.book-head div.label a.green::text').getall()
        words = response.css('div.book-head div.count span.num[id="word_info"]::text').get()
        # chapters_info = response.css('div.book-list dt span.info::text').getall()
        book_id=response.url.split('/')[-1][:-5]
        other_url = f'https://www.4yt.net/ck/book/{book_id}/databox?appKey=3156022953'
        meta = {
            'book_id':book_id,
            'title': title,
            'author': author,
            'tags': tags,
            'words': words,
            # 'chapters_info': chapters_info,
            'url': book_link,
            'approx_novel_start':approx_novel_start,
            'last_chapter_time':last_chapter_time,
            'status':status,
            'approx_num_chapts':approx_num_chapts
        }
        yield response.follow(url=other_url, callback=self.get_others, meta=meta)

    def get_others(self, response):
        meta_data = response.meta

        res_json = response.json()
        reads = res_json['data']['pv']
        total_recomendations = res_json['data']['recommentTicket']
        weekly_recomendations = res_json['data']['week']['recommentTicket']

        output = {
            'title': meta_data['title'],
            'book_id':meta_data['book_id'],
            'author': meta_data['author'],
            'tags': meta_data['tags'],
            'approx_num_chapts': meta_data['approx_num_chapts'],
            'status':meta_data['status'],
            'approx_novel_start':meta_data['approx_novel_start'],
            'last_chapter_time':meta_data['last_chapter_time'],
            'words': meta_data['words'],
            # 'volume-wise chapters-update-info': meta_data['chapters_info'],
            'url': meta_data['url'],
            'reads': reads,
            'total_recomendations': total_recomendations,
            'weekly_recomendations': weekly_recomendations
        }

        self.output.append(output)

    def closed(self, reason):
        df = pd.DataFrame(self.output)
        df.to_csv('4yt.csv', index=False)