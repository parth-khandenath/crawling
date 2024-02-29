import scrapy
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import time
import os
from csv import DictWriter


class Lightnovelworld(scrapy.Spider):
    name = 'light_novel_world'
    file_name = "light-novel-world.csv"
    start_urls = []
    df_header = {'id':[],'title':[],'url':[],'author':[],'rank':[],'rating':[],'views':[],'chapter_count':[],'bookmarked':[],'categories':[],'summary':[],'tags':[]}

    custom_settings = {
        # 'CONCURRENT_REQUESTS': 6,  # To avoid rate-limiting or server issues
        # 'DOWNLOAD_DELAY': 3,  # Add delay between requests
        'headers' : {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'lnusrconf=16%2Cdefault%2Cfalse%2Cblack%2Cpurple%2Cen%2C0%2C1; _ga=GA1.1.1055518345.1708922100; _lnvstuid=v2_2fde2eb59570e422a8322513e5277c44_0.6; lncoreantifrg=CfDJ8FTuPJ4Uz0dHhMCYxHc4GMOyZxzF-BlLc9aucUDrjF8dR4FhuBFloRRG0DWwOb_bQSUjjOifOxYXp7lBSy94BVgvH6D5D7O1plQOULmfSgNFeiZr9gguShaHQu9Vw0gWibFCVprrHpT5Ok-ydoVTjXI; cf_chl_3=dae42378e9b733c; _ga_ND87K88291=GS1.1.1708927617.2.1.1708930329.0.0.0; cf_clearance=p_focseqApsHANGIF5VE.5oiZNac_abNUg.XW1_C_8Y-1708930311-1.0-AQJDWuPhY0/LUeCOZ3g4ilF3ed9fOzOPUY+8S9pl5MqyLlLzWEu66Caig4LTAvSj4USEkRghhyI8RU+6kI/Zrxc=; cto_bundle=6jY-hF9zRGZicW4ycUhycFlRM09GMmFkR3ducXFBNEJOMmt2ZiUyQnkybU5mZE4ydkUydGVKWDdhRFd5bGkxNDhvNmpvalhVUGIlMkJRcnhZeDYxbXNnYUpOZkdhTDBKQ0lNMmclMkZMdzJvaFZYaWRLajJkRG5TR3BZJTJGQmtoJTJCJTJCNyUyRloxb0FKc2hEd1JJY0NmZ2xrWTJLZkxXWGpBdmIlMkZBamMlMkZsbzIwcEM0endDcWtqdFc4WFklM0Q',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"'
        }
    }

    def __init__(self):
        # options = uc.ChromeOptions() 
        # options.add_argument('--disable-blink-features=AutomationControlled')
        # options.add_argument('--headless')
        # options.add_argument('--cookie=lnusrconf=16%2Cdefault%2Cfalse%2Cblack%2Cpurple%2Cen%2C0%2C1; _ga=GA1.1.1055518345.1708922100; _lnvstuid=v2_2fde2eb59570e422a8322513e5277c44_0.6; lncoreantifrg=CfDJ8FTuPJ4Uz0dHhMCYxHc4GMOyZxzF-BlLc9aucUDrjF8dR4FhuBFloRRG0DWwOb_bQSUjjOifOxYXp7lBSy94BVgvH6D5D7O1plQOULmfSgNFeiZr9gguShaHQu9Vw0gWibFCVprrHpT5Ok-ydoVTjXI; cf_chl_3=dae42378e9b733c; _ga_ND87K88291=GS1.1.1708927617.2.1.1708930329.0.0.0; cf_clearance=p_focseqApsHANGIF5VE.5oiZNac_abNUg.XW1_C_8Y-1708930311-1.0-AQJDWuPhY0/LUeCOZ3g4ilF3ed9fOzOPUY+8S9pl5MqyLlLzWEu66Caig4LTAvSj4USEkRghhyI8RU+6kI/Zrxc=; cto_bundle=6jY-hF9zRGZicW4ycUhycFlRM09GMmFkR3ducXFBNEJOMmt2ZiUyQnkybU5mZE4ydkUydGVKWDdhRFd5bGkxNDhvNmpvalhVUGIlMkJRcnhZeDYxbXNnYUpOZkdhTDBKQ0lNMmclMkZMdzJvaFZYaWRLajJkRG5TR3BZJTJGQmtoJTJCJTJCNyUyRloxb0FKc2hEd1JJY0NmZ2xrWTJLZkxXWGpBdmIlMkZBamMlMkZsbzIwcEM0endDcWtqdFc4WFklM0Q')
        # options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
        # self.driver = uc.Chrome(options=options)
        
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
        # chrome_options.add_argument('--cookie=lnusrconf=16%2Cdefault%2Cfalse%2Cblack%2Cpurple%2Cen%2C0%2C1; _ga=GA1.1.1055518345.1708922100; _lnvstuid=v2_2fde2eb59570e422a8322513e5277c44_0.6; lncoreantifrg=CfDJ8FTuPJ4Uz0dHhMCYxHc4GMOyZxzF-BlLc9aucUDrjF8dR4FhuBFloRRG0DWwOb_bQSUjjOifOxYXp7lBSy94BVgvH6D5D7O1plQOULmfSgNFeiZr9gguShaHQu9Vw0gWibFCVprrHpT5Ok-ydoVTjXI; cf_chl_3=dae42378e9b733c; _ga_ND87K88291=GS1.1.1708927617.2.1.1708930329.0.0.0; cf_clearance=p_focseqApsHANGIF5VE.5oiZNac_abNUg.XW1_C_8Y-1708930311-1.0-AQJDWuPhY0/LUeCOZ3g4ilF3ed9fOzOPUY+8S9pl5MqyLlLzWEu66Caig4LTAvSj4USEkRghhyI8RU+6kI/Zrxc=; cto_bundle=6jY-hF9zRGZicW4ycUhycFlRM09GMmFkR3ducXFBNEJOMmt2ZiUyQnkybU5mZE4ydkUydGVKWDdhRFd5bGkxNDhvNmpvalhVUGIlMkJRcnhZeDYxbXNnYUpOZkdhTDBKQ0lNMmclMkZMdzJvaFZYaWRLajJkRG5TR3BZJTJGQmtoJTJCJTJCNyUyRloxb0FKc2hEd1JJY0NmZ2xrWTJLZkxXWGpBdmIlMkZBamMlMkZsbzIwcEM0endDcWtqdFc4WFklM0Q')
        self.driver = webdriver.Chrome(options=chrome_options)
        for pg in range(1,86):
            self.start_urls.append(f'https://www.lightnovelworld.co/browse/genre-all-25060123/order-popular/status-all?page={pg}') 
        print(self.start_urls)

    def append_list_as_row(self, list_of_elem):
        file_exists = os.path.isfile(self.file_name)
        with open(self.file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def parse(self, response):  #per page crawl
        time.sleep(10)
        return
        page_link=response.url
        print('page:',page_link)
        self.driver.get(page_link)
        book_links=self.driver.find_elements(By.CSS_SELECTOR,'h1.novel-title a')
        # links=response.css('.novel-title a::attr("href")').getall()
        for bl in book_links:
            link=bl.get_attribute('href')
            id=link.split('-')[-1]
            if link[:6]=='/novel':
                yield response.follow(url='https://www.lightnovelworld.co'+link, meta={'id':id, 'url':'https://www.lightnovelworld.co'+link}, callback=self.parse_book)
            else:
                yield response.follow(url=link, meta={'id':id, 'url':link}, callback=self.parse_book)

    def parse_book(self, response):
        meta=response.meta
        title=self.driver.find_element(By.CSS_SELECTOR,'.novel-title').text
        author=self.driver.find_element(By.CSS_SELECTOR,'div.author a.property-item span').text
        rank=self.driver.find_element(By.CSS_SELECTOR,'div.author a.property-item span').text
        stats=self.driver.find_elements(By.CSS_SELECTOR,'strong')
        rank=stats[0].text
        rating=stats[1].text
        chapter_count=stats[2].text
        views=stats[3].text
        bookmarked=stats[4].text
        status=stats[5].text

        category_eles=self.driver.find_elements(By.CSS_SELECTOR,'li .property-item')
        categories=[]
        for ele in category_eles:
            categories.append(ele.text)

        summary=''
        p_eles=self.driver.find_elements(By.CSS_SELECTOR,'.summary p')
        for ele in p_eles:
            summary+=ele.text

        tags=[]
        tag_eles=self.driver.find_elements(By.CSS_SELECTOR,'ul.content li')
        for ele in tag_eles:
            tags.append(ele.text)

        data = {
            'id': 'lightnovelworld-'+meta['id'],
            'title':title,
            'url':meta['url'],
            'author':author,
            'rank':rank,
            'rating':rating,
            'views':views,
            'chapter_count':chapter_count,
            'bookmarked':bookmarked,
            'categories':categories,
            'summary':summary,
            'tags':tags
        }
        self.append_list_as_row(data)

if __name__ == "__main__":
    from scrapy.crawler import CrawlerProcess
    process = CrawlerProcess()
    print('#########')
    process.crawl(Lightnovelworld)
    print('#########')
    process.start()
    print('#########')
