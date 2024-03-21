import scrapy
import pandas as pd
# class mkzhanSpider(scrapy.Spider) :
#     name = 'mkzhan_comics'
#     def __init__(self, **kwargs) :
#         df_header = {
#             'title':[],
#             'url':[],
#             'author':[],
#             'theme':[],
#             'collections':[],
#             'popularity':[],
#             'monthly_Votes':[] ,
#             'chapter_Count':[] ,
#             'rating':[],
#             'no_Of_Ratings':[],
#             'introduction':[],
#             }
#         self.df=pd.DataFrame(df_header)
#         self.start_urls = [ ]
#         for i in range(1,2):
#             self.start_urls.append('https://www.mkzhan.com/category/?page='+str(i))
#         custom_settings={
#             'CONCURRENT_REQUESTS':1,
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
#             }
#     def parse(self,response) :
#         file_name = 'mkzhan_comics'
#         sheet = 'mkzhan_listing'
#     def page_parse(self,response) :
#         links=response.css('.comic__title a::attr(href)').getall()
#         for l in links:
#                 booklink='https://www.mkzhan.com'+l
#                 yield response.follow(url=booklink,callback=self.parse_book,meta={'bl':booklink})
#     def parse_book(self,response): #on book page
#         url=response.meta['bl']
#         title=response.css('.j-comic-title font font::text').get()
#         author=response.css('.name font font::text').get()
#         stats=response.css('.text font font::text').getall()
#         theme=response.css('.text:nth-child(1) b font font::text').getall()
#         collections=response.css('.text:nth-child(2) font  font::text').get()
#         popularity=response.css('.text~ .text+ .text font  font::text').get()
#         monthly_Votes=response.css('.btn--ticket font  font::text').get()
#         chapter_Count=response.css('.id-1036532 font  font::text').get()
#         rating=response.css('.layui-inline font font::text').get()
#         no_Of_Ratings=response.css('.rate-count .num font font::text').get()
#         introduction=response.css('.intro font font::text').get()
#         print(url,title,author,stats,theme,collections,popularity,monthly_Votes,chapter_Count,rating,no_Of_Ratings,introduction)
        # like this
        # do monthly_votes  #do chapter_count  #do rating and no. of ratings # introduction
import pandas as pd
import scrapy

class mkzan(scrapy.Spider):
    name = 'mkhzan'
    def __init__(self, **kwargs):
        df_header={'Title':[],
                    'URL':[],
                    'Author/Publisher':[],
                    'Theme':[],
                    'Collections':[],
                    'Popularity':[],
                    'Monthly Votes':[] ,
                    'Chapter Count':[] ,
                    'Rating + No. of Ratings':[],
                    'Introduction':[],
                    }
        self.df=pd.DataFrame(df_header)
        self.start_urls = [ ]
        for i in range(1,75):
            self.start_urls.append('https://www.mkzhan.com/category/?page='+str(i))     
        
                
    custom_settings={
        'CONCURRENT_REQUESTS':1
    }
    
    def parse(self,response): #on catalog page
        links=response.css('.comic__title a::attr(href)').getall()
        for l in links:
            booklink='https://www.mkzhan.com'+l
            yield response.follow(url=booklink,callback=self.parse_book,meta={'bl':booklink})
    
    def parse_book(self,response): #on book page
        url=response.meta['bl']
        title=response.css('.j-comic-title font font::text').get()
        author=response.css('.name font font::text').get()   
        stats=response.css('.text font font::text').getall()
        print(title,author,stats)
        # theme=stats[1]
        # collection=stats[3]
        # popularity=stats[5]
        # like this
        # do monthly_votes  #do chapter_count  #do rating and no. of ratings # introduction