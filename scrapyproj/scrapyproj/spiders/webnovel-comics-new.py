import scrapy
import re
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import time

#for comics
import re

def extract_hashtags(text):
    try:
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    except:
        return []

class webnovelcomicspider(scrapy.Spider):
    name = 'webnovel_comic_spider'
    file_name = "webnovel-comics.csv"
    start_urls = ['https://www.webnovel.com/stories/comic']
    df_header = { 'bookName':[], 'url':[], 'genre':[], 'status':[],'lastChapterTime':[], 'views':[], 'chapterCount':[], 'firstChapterDate':[], 'description':[], 'tags':[], 'rating':[], 'numOfRatings':[]}
    # Headers = {"book name":[],"URL":[],"Genre":[],"Author Name":[],"Chapter Number":[],"Views":[],"Rating":[],"Number of ratings":[],"Status":[],"latest chapter":[],"latest chapter time":[],"first chapter time":[],"Tags":[],"Book Available for comic":[]}
    try:
        df=pd.read_csv(file_name)
    except:
        df = pd.DataFrame(df_header)

    def parse(self, response):
        cookie = response.headers.getlist(b'Set-Cookie')[0]
        cookie = str(cookie)
        self.driver = uc.Chrome()
        csrf = cookie.split(';')[0].split('=')[-1]
        for i in range(1,50):  
            p = i * 100
            # url = f"https://www.webnovel.com/go/pcm/category/getRankList?_csrfToken={csrf}&pageIndex={str(i)}" + self.u
            page_url = f'https://www.webnovel.com/go/pcm/category/categoryAjax?_csrfToken={csrf}&pageIndex={str(i)}&categoryId=0&categoryType=2&bookStatus=0&orderBy=1'
            # print(url)

            yield response.follow(url=page_url, priority=-p, meta={'csrf': csrf, 'p': -p}, callback=self.parse_page)

    def parse_page(self, response):
        csrf = response.meta['csrf']
        p = response.meta['p']
        book_items = response.json()['data']['items']
        for i in range(len(book_items)):
            book_id = book_items[i]['bookId']
            book_name = book_items[i]['bookName']
            description = book_items[i]['description']
            categoryName = book_items[i]['categoryName']
            author = book_items[i]['authorName']
            rating = book_items[i]['totalScore']
            chapter_count = book_items[i]['chapterNum']
            tagslst = book_items[i]['tagInfo']
            tags = [tag['tagName'] for tag in tagslst]
            if tags==[]:
                tags=extract_hashtags(description)
            book_url = f'https://www.webnovel.com/go/pcm/bookReview/get-reviews?_csrfToken={csrf}&bookId={book_id}&pageIndex=1&pageSize=30&orderBy=1&novelType=0&needSummary=1&_=1696419259573'
            meta = {
                'book_id': book_id,
                'book_name': book_name,
                'author': author,
                'categoryName': categoryName,
                'description': description,
                'tags': tags,
                'rating':rating,
                'chapter_count':chapter_count
            }
            yield response.follow(url=book_url, priority=p - i, meta=meta, callback=self.parse_book)

    def parse_book(self, response):
        baseInfo = response.json()['data']['baseInfo']
        views = baseInfo['pvNum']
        meta = response.meta
        stats = response.json()['data']['bookStatisticsInfo']
        totalReviewNum = stats['totalReviewNum']
        data = {
            'book_id': meta['book_id'],
            'book_name': meta['book_name'],
            'author': meta['author'],
            'categoryName': meta['categoryName'],
            'description': meta['description'],
            'rating': meta['rating'],
            'totalReviewNum': totalReviewNum,
            'views': views,
            'chapter_count': meta['chapter_count'],
            'tags': meta['tags'],
            'url': 'https://www.webnovel.com/comic/' + meta['book_id']    #wrong
        }

        
        yield response.follow(url=data['url'], meta=data, callback=self.extract_chapters)


    def extract_chapters(self, response):
        meta = response.meta
        data = {
            'book_id': meta['book_id'],
            'book_name': meta['book_name'],#name
            'author': meta['author'],#author name
            'categoryName': meta['categoryName'],#genre
            'description': meta['description'],
            'chapter_count': meta['chapter_count'],
            'rating': meta['rating'],#rating
            'total reviews': meta['totalReviewNum'],#number of rating
            'views': meta['views'],#views
            'tags': meta['tags'],
            'url': meta['url']#url
        }
        
        r = response.text
        completed = 'Not available'
        if '<span>Completed</span>' in r:
            completed = 'Completed'
        
        # bookLink = response.css('.m-lang a::attr("href")').get()
        # if bookLink is None:
        #     bookLink="No book present"
        # else:
        #     bookLink= 'https://www.webnovel.com' + bookLink


        # s = re.findall(r'chapterNum.*?,', r)
        # lst = s
        # text = lst[0]
        # chapter_num = int(text.split(":")[1].strip(",}"))
        # data['chapterNum'] = chapter_num #chapter num
        
        ur = meta['url']+'/catalog'
        self.driver.get(ur)
        time.sleep(7)
        soup = bs(self.driver.page_source,"lxml")
        latest_chapter_time = soup.select_one('.c_s.ml8').text
        first_chapter_time = soup.select_one('small.c_s.fs12.lh16').text
        self.df.loc[len(self.df.index)] = [meta['book_name'],meta['url'],meta['categoryName'],completed,latest_chapter_time,meta['views'],meta['chapter_count'],first_chapter_time,meta['description'],str(meta['tags']),meta['rating'],meta['totalReviewNum']]
        self.df.to_csv(self.file_name,index=False)
        # Titles list in Ranking Order
        # Title Name
        # URL
        # Genre 
        # Author Name
        # Chapter Number
        # Views
        # Rating
        # Number of Ratings
        # Status
        #Latest Chapter number
        # Latest Chapter Release Date
        # Chapter 1: Launch Year
        #Tags
        # Book Available for comic