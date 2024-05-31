import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import time
import ssl
import pandas as pd
import scrapy


ssl._create_default_https_context = ssl._create_unverified_context
class joyread(scrapy.Spider):
    name='joyread_werewolf'
    start_urls=[]
    def __init__(self):
        df_header = {
            'book_id':[],
            'booklink':[],
            'title':[],
            'author':[],
            'genre':[],
            'status':[],
            'chapters':[],
            'reads':[],
            'likes':[] ,
            'tags':[] ,
            'description':[],
            }
        self.df=pd.DataFrame(df_header)

        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
        driver = uc.Chrome(options=chrome_options)

        driver.get('https://www.joyread.com/genre/11-Werewolf-hot')
        for page in range(1,106):
            custom_settings={
                'CONCURRENT_REQUESTS':5,
                'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
                }
            time.sleep(5)
            atags=driver.find_elements(By.CSS_SELECTOR,'a.m-list')
            
            for atag in atags:
                #atag = re.sub(r'\D', '', atag)
                self.start_urls.append(atag.get_attribute('href'))

            page_buttons=driver.find_elements(By.CSS_SELECTOR,'li.number')
            for button in page_buttons:
                if str(page+1) in button.text:
                    button.click()
                    break

        driver.close()

    def parse(self, response):
        book_id="joyread-"+(response.url).split('/')[-1].split('-')[0]
        booklink=response.url
        title=response.css('div.info-title::text').get()
        author=response.css('.info-author span::text').get()
        genre="werewolf"
        status=(response.css('.info-chapter span:nth-child(1)::text').get().replace("|",""))
        chapters=(response.css('span+ span::text').get()).replace("| Chapter ","")
        reads=response.css('.info-like-list:nth-child(1) .info-like-top::text').get()
        likes=response.css('.info-like-list+ .info-like-list .info-like-top::text').get()
        tags=response.css('.wdb-mid .wdb-tag-list::text').getall()
        tags="-".join(tags)
        description=response.css('.wdb-bot::text').get()

        #print(book_id,booklink,title,author,genre,status,chapters,reads,likes,tags,description)


        self.df.loc[len(self.df.index)] = [book_id,booklink,title,author,genre,status,chapters,reads,likes,tags,description]
        
        self.df.to_csv(f'{self.name}.csv',index=False)