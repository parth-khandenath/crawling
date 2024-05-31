import scrapy
from scrapy.crawler import CrawlerProcess
import re
import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import time

class PowertoolListingWebnovelComicsSpider(scrapy.Spider):
    name="listing_WebnovelComics"
    order_map={"most-popular":1, "recommended":2, "most-collections":3}
    genre_map={"all":0,"Action":60002,"Fantasy":-1,"Harem":60017,"Magic":-1,"Eastern":60006,"Sci-Fi":60004,"Sports":-1,"Inspiring":-1,"Comedy":60011,"Drama":-1,"Mystery":60008, "Romance":60003, "LGBT+":60029, "Urban":60005, "Transmigration":60012, "School":60007, "Adventure":60014, "History":60018, "Horror":60015, "Wuxia":-1, "Slice-of-Life":-1, "Cooking":-1,  "Diabolical":-1}
    start_urls = ['https://www.webnovel.com/stories/comic']
    df_header = { 'bookName':[], 'url':[], 'genre':[], 'status':[],'lastChapterTime':[],'publisher':[], 'views':[], 'chapterCount':[], 'firstChapterDate':[], 'description':[], 'tags':[], 'rating':[], 'numOfRatings':[], 'translationQuality':[], 'storyDevelopment':[], 'characterDesign':[]}

    def __init__(self, **kwargs):
        self.genre=kwargs['genre']
        self.order=kwargs['order']
        self.output_dict = kwargs['output_dict']
        self.data_list = []
        self.file_name = f"webnovel-comics-{self.genre}-{self.order}"
        self.df = pd.DataFrame(self.df_header)

    def parse(self, response):
        cookie = response.headers.getlist(b'Set-Cookie')[0]
        cookie = str(cookie)
        options = uc.ChromeOptions()
        options.add_argument('--headless')
        self.driver = uc.Chrome(options = options)
        csrf = cookie.split(';')[0].split('=')[-1]
        for i in range(1,50):  
            p = i * 100
            page_url = f'https://www.webnovel.com/go/pcm/category/categoryAjax?_csrfToken={csrf}&pageIndex={str(i)}&categoryId={self.genre_map[self.genre]}&categoryType=2&bookStatus=0&orderBy={self.order_map[self.order]}'

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
            if categoryName.lower().replace('-','').replace(' ','')=='sliceoflife':
                categoryName='Slice-of-Life'
            author = book_items[i]['authorName']
            rating = book_items[i]['totalScore']
            chapter_count = book_items[i]['chapterNum']
            tagslst = book_items[i]['tagInfo']
            tags = [tag['tagName'] for tag in tagslst]
            if tags==[]:
                tags=self.extract_hashtags(description)
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
        translationQuality=stats['translationQuality']
        storyDevelopment=stats['storyDevelopment']
        characterDesign=stats['characterDesign']
        data = {
            'book_id': meta['book_id'],
            'book_name': meta['book_name'],
            'author': meta['author'],
            'categoryName': meta['categoryName'],
            'description': meta['description'],
            'rating': meta['rating'],
            'totalReviewNum': totalReviewNum,
            'views': views,
            'translationQuality':translationQuality,
            'storyDevelopment':storyDevelopment,
            'characterDesign':characterDesign,
            'chapter_count': meta['chapter_count'],
            'tags': meta['tags'],
            'url': 'https://www.webnovel.com/comic/' + meta['book_id']
        }

        yield response.follow(url=data['url'], meta=data, callback=self.extract_chapters)

    def extract_chapters(self, response):
        meta = response.meta

        r = response.text
        lst= response.css('.mb12.lh24.c_000.fw400::text').getall()
        publisher=''.join(lst)
        completed = 'Not available'
        if '<span>Completed</span>' in r:
            completed = 'Completed'

        ur = meta['url']+'/catalog'
        self.driver.get(ur)
        time.sleep(7)
        soup = bs(self.driver.page_source,"lxml")
        latest_chapter_time = soup.select_one('.c_s.ml8').text
        first_chapter_time = soup.select_one('small.c_s.fs12.lh16').text
        self.df.loc[len(self.df.index)] = [meta['book_name'],meta['url'],meta['categoryName'],completed,latest_chapter_time,publisher,meta['views'],meta['chapter_count'],first_chapter_time,meta['description'],str(meta['tags']),meta['rating'],meta['totalReviewNum'],meta['translationQuality'],meta['storyDevelopment'],meta['characterDesign']]
        # self.df.to_csv(f"{self.file_name}.csv",index=False)

    def closed(self, reason):
        self.driver.close()
        self.output_dict[self.file_name]=self.df
        
    def extract_hashtags(self, text):
        try:
            hashtags = re.findall(r'#\w+', text)
            return hashtags
        except:
            return []

def main(output_dict):
    combinations=[["Eastern","most-popular"],["Eastern","recommended"]]#,["Eastern","most-collections"],["Sci-Fi","most-popular"],["Sci-Fi","recommended"],["Sci-Fi","most-collections"],["Comedy","most-popular"],["Comedy","recommended"],["Comedy","most-collections"],["Mystery","most-popular"],["Mystery","recommended"],["Mystery","most-collections"],["Romance","most-popular"],["Romance","recommended"],["Romance","most-collections"],["LGBT+","most-popular"],["LGBT+","recommended"],["LGBT+","most-collections"],["Urban","most-popular"],["Urban","recommended"],["Urban","most-collections"],["Transmigration","most-popular"],["Transmigration","recommended"],["Transmigration","most-collections"],["School","most-popular"],["School","recommended"],["School","most-collections"],["Adventure","most-popular"],["Adventure","recommended"],["Adventure","most-collections"],["History","most-popular"],["History","recommended"],["History","most-collections"],["Horror","most-popular"],["Horror","recommended"],["Horror","most-collections"]]
    # ol=["most-popular","recommended","most-collections"]
    process = CrawlerProcess({'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                            #   'LOG_LEVEL': 'INFO'
                              })

    def next_crawl(i):
        try:
            # if i>28:
            a = process.crawl(PowertoolListingWebnovelComicsSpider, genre=combinations[i][0], order=combinations[i][1], output_dict=output_dict)
            a.addCallback(lambda _: next_crawl(i + 1))
            # else:
            #     next_crawl(i+1)
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
    output_dict = {"output":None}
    main(output_dict)