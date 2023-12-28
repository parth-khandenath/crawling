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
        'CONCURRENT_REQUESTS': 100,
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter'
    }

    def __init__(self, **kwargs):
        self.output_dict = {}
        self.priority = 1000000
        self.output = []

    def parse(self, response):
        base_url = 'https://www.4yt.net'
        urls = response.css('a.bookcover::attr(href)').getall()

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
        df.to_csv('4yt-new.csv', index=False)