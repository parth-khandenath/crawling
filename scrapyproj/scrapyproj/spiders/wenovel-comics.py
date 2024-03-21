import scrapy
import re
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import time

#for comics
import re

def extract_hashtags(text):
    hashtags = re.findall(r'#\w+', text)
    return hashtags

class WebnovelListingSpider(scrapy.Spider):
    name = 'Webnovel_comics_Listing'
    file_name = "Webnovel 'Comic' Female 'Trending' Rank All Time"
    start_urls = ['https://www.webnovel.com/stories/novel']
    u = '&rankId=comic_best_sellers&listType=0&type=2&rankName=Trending&timeType=1&sex=2'
    Headers = {"book name":[],"URL":[],"Genre":[],"Author Name":[],"Chapter Number":[],"Views":[],"Rating":[],"Number of ratings":[],"Status":[],"latest chapter":[],"latest chapter time":[],"first chapter time":[],"Tags":[],"Book Available for comic":[]}
    ans = pd.DataFrame(Headers)
    def parse(self, response):
        cookie = response.headers.getlist(b'Set-Cookie')[0]
        cookie = str(cookie)
        self.driver = uc.Chrome()
        csrf = cookie.split(';')[0].split('=')[-1]
        for i in range(1, 11):
            p = i * 100
            url = f"https://www.webnovel.com/go/pcm/category/getRankList?_csrfToken={csrf}&pageIndex={str(i)}" + self.u
            print(url)

            yield response.follow(url=url, priority=-p, meta={'csrf': csrf, 'p': -p}, callback=self.parse_page)

    def parse_page(self, response):
        csrf = response.meta['csrf']
        p = response.meta['p']
        book_items = response.json()['data']['bookItems']
        for i in range(len(book_items)):
            book_id = book_items[i]['bookId']
            book_name = book_items[i]['bookName']
            author = book_items[i]['authorName']
            categoryName = book_items[i]['categoryName']
            description = book_items[i]['description']
            amount = ''
            # amount=book_items[i]['amount']    #this number is not the actual views 
            tags = book_items[i]['tagInfo']
            tags = [tag['tagName'] for tag in tags]
            if tags==[]:
                tags=extract_hashtags(description)
            url = f'https://www.webnovel.com/go/pcm/bookReview/get-reviews?_csrfToken={csrf}&bookId={book_id}&pageIndex=1&pageSize=30&orderBy=1&novelType=0&needSummary=1&_=1696419259573'
            meta = {
                'book_id': book_id,
                'book_name': book_name,
                'author': author,
                'categoryName': categoryName,
                'description': description,
                'amount': amount,
                'tags': tags
            }
            yield response.follow(url=url, priority=p - i, meta=meta, callback=self.parse_book)

    def parse_book(self, response):
        baseInfo = response.json()['data']['baseInfo']
        views = baseInfo['pvNum']
        meta = response.meta
        stats = response.json()['data']['bookStatisticsInfo']
        rating = stats['totalScore']
        totalReviewNum = stats['totalReviewNum']
        data = {
            'book_id': meta['book_id'],
            'book_name': meta['book_name'],
            'author': meta['author'],
            'categoryName': meta['categoryName'],
            'description': meta['description'],
            'amount': meta['amount'],
            'rating': rating,
            'totalReviewNum': totalReviewNum,
            'views': views,
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
            'bookmarks': meta['amount'],
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
        
        bookLink = response.css('.m-lang a::attr("href")').get()
        if bookLink is None:
            bookLink="No book present"
        else:
            bookLink= 'https://www.webnovel.com' + bookLink


        s = re.findall(r'chapterNum.*?,', r)
        lst = s
        text = lst[0]
        chapter_num = int(text.split(":")[1].strip(",}"))
        data['chapterNum'] = chapter_num #chapter num
        
        ur = meta['url']+'/catalog'
        self.driver.get(ur)
        time.sleep(7)
        soup = bs(self.driver.page_source,"lxml")
        latest_chapter = soup.select_one('.lst-chapter').text
        latest_chapter_time = soup.select_one('.c_s.ml8').text
        first_chapter_time = soup.select_one('small.c_s.fs12.lh16').text
        self.ans.loc[len(self.ans.index)] = [meta['book_name'],meta['url'],meta['categoryName'],meta['author'],chapter_num,meta['views'],meta['rating'],meta['totalReviewNum'],completed,latest_chapter,latest_chapter_time,first_chapter_time,str(meta['tags']),bookLink]
        self.ans.to_csv(f'{self.file_name}.csv',index=False)
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
