import time
import scrapy
import undetected_chromedriver as uc
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup



class wehearfm(scrapy.Spider):
    name="wehearfm"
    start_urls=[]
    df_header = {
        "id":[], "title": [],"url": [], "author": [], "narrators":[], "summary": [], "listeners": [],
        "duration": [], "episodes": [], "status": [], "tags": []
    }
    custom_settings = { 
        'CONCURRENT_REQUESTS': 6
    }

    def __init__(self):
        cat_links =[]
        cat_endpts=['/1-best-audiobooks',"/2-editors'-picked-audiobooks",'/3-best-completed-audiobooks','/4-best-new-audiobooks','/5-popular-audiobook-series','/6-most-searched-audiobooks','/7-audiobooks-in-fashion','/8-best-saga-audiobooks']
        base_url='https://wehearfm.com/hot-collections'
        for ce in cat_endpts:
            for i in range(1,4):
                cat_links.append(base_url+ce+f'?page={str(i)}')

        options = uc.ChromeOptions()
        options.add_argument('--headless')  
        driver = uc.Chrome(options=options)
        
        for cl in cat_links:
            driver.get(cl)
            time.sleep(5)
            soup=BeautifulSoup(driver.page_source,'lxml')
            bl_eles=soup.select('.hot-collections_detail-book-desc__rMZqA a')
            for ele in bl_eles:
                if ele.get('href'):
                    self.start_urls.append("https://wehearfm.com"+ele.get('href'))
        try:
            self.df=pd.read_csv("wehearfm.csv")
        except:
            self.df=pd.DataFrame(self.df_header)

        driver.close()

    def parse(self,response):
        url=response.url
        # print(url)
        id='wehearfm-'+url.split('/')[-1]
        title=response.css('h1.book_book-name__nnzml::text').get()
        try:
            author=response.css('label.book_book-author__kMqPw::text').getall()[1]
        except:
            author='NA'
        try:
            narrators=response.css('label.book_book-narrater__uT6Kl::text').getall()[1]
        except:
            narrators='NA'
        stats=response.css('.book_book-total__7U7go span::text').getall()
        duration=stats[1]
        totalepis=stats[2]
        status=stats[4]
        summary=response.css('.book_merchant-desc__Me3xN::text').get()
        tags=response.css(".book_book-d-tags__P7sbZ li::text").getall()
        tags="-".join(tags)
        listeners=response.css(".book_book-like__CfBWn::text").get()
        listeners=self.process(listeners)
        
        self.df.loc[len(self.df.index)]=[id,title,url,author,narrators,summary,listeners,duration,totalepis,status,tags]
        self.df.to_csv("wehearfm.csv",index=False)
        
    def process(self,num):
        try:
            num=str(num)
            if num[-1]=='M':
                num=int(float(num[:-1])*1000000)
            elif num[-1]=='K':
                num=int(float(num[:-1])*1000)
            return num
        except Exception as e:
            print(e)
            return 'NA'

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(wehearfm)
    process.start()