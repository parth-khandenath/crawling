import pandas as pd
from scrapy.crawler import CrawlerProcess
import scrapy
class AllnovelSpider(scrapy.Spider):
    name = 'all_novel_spider'
    output = []
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1,
        'USER_AGENT':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    }

    def __init__(self, **kwargs):
        # self.start_urls = [' https://allnovelupdates.com/genres/Tragedy/ ' ]   #[kwargs['site_url']] 
        self.start_urls = ['https://www.mtlnovel.com/genre/josei/' ]   #[kwargs['site_url']] 
        # self.book_name =  'All Novel Updates- Genre - Tragedy'    #kwargs['name']
        self.book_name =  'MTL Novel Updates- Genre - Horror'    #kwargs['name']
        # self.output_dict = kwargs['output_dict']
        self.output = []

    def parse(self, response):
        # last_page_url = response.css('div.pages ul li a::attr(href)').getall()[-1]
        try:
            last_page_url = response.css('div#pagination a::attr(href)').getall()[-1]
            # "/horror/23/"   ['','23','']
            last_page_number = last_page_url.split('/')[-2]
            print("###### {} #####".format(last_page_number))
        except Exception as err:
            print("errrrrrrr")
            print(err)
        # if last_page_number:
        #     last_page_number = int(last_page_number)
        # for i in range(1, last_page_number + 1):
        #     url = response.url + f"{str(i)}"
        #     yield response.follow(url=url, callback=self.parse_page, priority=-i*100, meta={'p':-i*100})

    def parse_page(self, response):
        p=int(response.meta['p'])
        urls = response.css('div.ul-list1 div.li-row div.con div.pic a::attr(href)').getall()
        count=0
        for url in urls:
            yield response.follow(url=url, callback=self.parse_book, priority=p-count)
            count-=1


    def parse_book(self, response):
        # https://allnovelupdates.com/book/since-the-red-moon-appeared
        data = response.css('div.item div.right')
        if not data:
            print('no data')
            return

        title = response.css('h1::text').get()
        url = response.url
        last_chapter = response.css('.m-newest1 li:nth-child(1) a::text').get()
        last_page_chapters = response.css('#indexselect option::text').getall()[-1]
        try:
            vote_rating = response.css('p.vote::text').getall()[0]
            rating = vote_rating.split('/')[0].strip()
            votes = vote_rating.split('(')[1].split('vote')[0].strip()

        except:
            vote_rating = 'NA'

        if len(data) == 5:
            alternate_title = data[0].css('span.s1 ::text').get()
            author = data[1].css('a::text').get()
            platform = data[3].css('span.s1 ::text').get()
            status = data[4].css('span.s1 a::text').get()
            tags = data[2].css('a::text').getall()
            tags = "-".join(tags)
        elif len(data) == 4:
            alternate_title = 'NA'
            author = data[0].css('a::text').get()
            platform = data[2].css('span.s1 ::text').get()
            status = data[3].css('span.s1 a::text').get()
            tags = data[1].css('a::text').getall()
            tags = "-".join(tags)
        else:
            print(len(data), 'error')

        self.output.append({
            "Title name": title,
            "Alternate Title": alternate_title,
            "URL": url,
            "Platform": platform,
            "Status": status,
            "Genre": tags,
            "Author": author,
            "Last_Chapter_name": last_chapter,
            "Last_section_chapters":last_page_chapters,
            "rating /5": rating,
            "votes (rating)": votes
        })


    def closed(self, reason):
        df = pd.DataFrame(self.output)
        df.to_csv( f"{self.book_name}.csv", index=False)