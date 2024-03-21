import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import scrapy

class joyread(scrapy.Spider):
    name='joyread'
    start_urls=[]
    def __init__(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
        driver = uc.Chrome(options=chrome_options)

        driver.get('https://www.joyread.com/genre/11-Werewolf-hot')
        for page in range(1,4):
            time.sleep(9)
            atags=driver.find_elements(By.CSS_SELECTOR,'a.m-list')
            
            for atag in atags:
                self.start_urls.append(atag.get_attribute('href'))

            page_buttons=driver.find_elements(By.CSS_SELECTOR,'li.number')
            for button in page_buttons:
                if str(page+1) in button.text:
                    button.click()
                    break

        driver.close()

    def parse(self, response):
        booklink=response.url
        title=response.css('div.info-title::text').get()
        author=response.css('.info-author span::text').get()
        genre= "werewolf"
        status=response.css('.info-chapter span:nth-child(1)::text').get()
        chapters=response.css('span+ span::text').get()
        reads=response.css('.info-like-list:nth-child(1) .info-like-top::text').get()
        likes=response.css('.info-like-list+ .info-like-list .info-like-top::text').get()
        tags=response.css('div.wdb-mid > div.wdb-tag-list::text').get()
        description=response.css('.wdb-bot::text').get()
        print(booklink,title,author,genre,status,chapters,reads,likes,tags,description)

    
if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    process.crawl(joyread)
    process.start()