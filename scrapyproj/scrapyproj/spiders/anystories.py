import scrapy
import pandas as pd
import json

class anystories_manyP(scrapy.Spider):
    name = 'anystories_manyP'
    start_urls = [
        'https://m.anystories.app/search?keywords=A&page=1'   
    ]
    custom_settings={
        'CONCURRENT_REQUESTS':1,
        'headers' : {
                        'accept': '*/*',
                        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
                        'cookie': 'sajssdk_2015_cross_new_user=1; _ga=GA1.1.1965478066.1715578955; afUserId=ac9117f4-a858-4c20-b32c-38b6d0c1768f-p; AF_SYNC=1715578956342; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218f707962804c7-0c3a4b2646ef7f-26001d51-1327104-18f70796281a7f%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22identities%22%3A%22eyIkaWRlbnRpdHlfY29va2llX2lkIjoiMThmNzA3OTYyODA0YzctMGMzYTRiMjY0NmVmN2YtMjYwMDFkNTEtMTMyNzEwNC0xOGY3MDc5NjI4MWE3ZiJ9%22%2C%22history_login_id%22%3A%7B%22name%22%3A%22%22%2C%22value%22%3A%22%22%7D%2C%22%24device_id%22%3A%2218f707962804c7-0c3a4b2646ef7f-26001d51-1327104-18f70796281a7f%22%7D; _ga_C65LEXCX0C=GS1.1.1715585211.2.1.1715586032.0.0.0',
                        'newrelic': 'eyJ2IjpbMCwxXSwiZCI6eyJ0eSI6IkJyb3dzZXIiLCJhYyI6IjM1NzM2MjMiLCJhcCI6IjExMjAxMzk2MTkiLCJpZCI6IjdmOTBjMjRkNWMxODNjM2QiLCJ0ciI6IjExMDBiYTc3ZTk4ZmU2NGY5YWQzNTIzZWIzNjljYmQ0IiwidGkiOjE3MTU1ODYwMzI5NTB9fQ==',
                        'priority': 'u=1, i',
                        'referer': 'https://m.anystories.app/search?keywords=A&page=1',
                        'sec-ch-ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
                        'sec-ch-ua-mobile': '?0',
                        'sec-ch-ua-platform': '"Windows"',
                        'sec-fetch-dest': 'empty',
                        'sec-fetch-mode': 'cors',
                        'sec-fetch-site': 'same-origin',
                        'traceparent': '00-1100ba77e98fe64f9ad3523eb369cbd4-7f90c24d5c183c3d-01',
                        'tracestate': '3573623^@nr=0-1-3573623-1120139619-7f90c24d5c183c3d----1715586032950',
                        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
                        'x-nextjs-data': '1'
                    }
    }
    sheet = 499
    df_header = {"book_id":[],"book_name":[],"author":[],"description":[],"completed":[],"total words":[],"hots":[],"views":[],"tags":[],"no of chapters":[],"latest chapter":[],"link":[]}
    file_name='anystories'
    ans = pd.DataFrame(df_header)
    cup=100000
    current_page=1
    page_upto=8  #370/50  total books mentioned in site/books per page. Check for changes

    def parse(self,response):
        count=0
        data = response.css('.undefined h3 a::attr("href")').getall()
        for link in data:
            url='https://m.anystories.app/_next/data/AqiNanou9NHe1rCnReu-j'  +  link  +  '/chapters.json'
            count+=1
            yield response.follow( url, callback=self.page, priority=self.cup - count)
        self.cup-=count
        if self.current_page<=self.page_upto:
            self.current_page+=1
            next_url = f'https://m.anystories.app/search?keywords=A&page={self.current_page}'
            yield response.follow( next_url, callback=self.parse)
    
    def page(self,response):
       
        book_items = response.json()['pageProps']['bookInfo']
        chapter_items = response.json()['pageProps']['chapters']
        

        book_id = book_items['book']['id']
        book_name =  book_items['book']['title']  #name
        author = book_items['author']['name'] #author name
        description = book_items['book']['description']
        completed = book_items['book']['completed']
        words_total = book_items['book']['words']
        hots = book_items['statistics']['hot']   #likes
        views = book_items['statistics']['views']
        tags = book_items['tags']
        tags = str([ tag['name'] for tag in tags])  #genre

        chapter_num = chapter_items[-1]['order']
        latest_chapter = chapter_items[-1]['title']
        url = 'https://m.anystories.app'   + (response.json()['pageProps']['path']).rsplit('/',1)[0]   

        {"book_id":[],"book_name":[],"author":[],"description":[],"completed":[],"total words":[],"hots":[],"views":[],"tags":[],"no of chapters":[],"latest chapter":[],"link":[],}
        

        self.ans.loc[len(self.ans.index)] = [book_id, book_name, author, description, completed, words_total, hots, views, tags, chapter_num, latest_chapter, url ]
        self.ans.to_csv(f'{self.file_name}.csv',index=False)

#book_id, book_name, author, description, completed, words_total, hots, views, tags, chapter_num, latest_chapter, url 