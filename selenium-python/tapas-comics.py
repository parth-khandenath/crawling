import scrapy
import pandas as pd
from scrapy.crawler import CrawlerProcess
from datetime import datetime


class TapasSpider(scrapy.Spider):
    name = 'tapas_spider'
    genre="Science Fiction"   #change here
    genre_map={"all":0,"Romance Fantasy":29,"Action Fantasy":30, "Science Fiction":4, "Fantasy":3}
    output = []
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1000,
    }

    def start_requests(self):

        for i in range(1, 1300):  #1300  is a safe number, all genres don't have more than these many pages

            url = f"https://tapas.io/comics?b=ALL&g={self.genre_map[self.genre]}&f=NONE&s=LIKE&pageNumber={i}&pageSize=20"

            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):

        urls = response.css('a.thumb::attr(href)').getall()

        for i in urls:
            url = "https://tapas.io" + i + "/info"
            idd=i.split('/')[-1]
            yield scrapy.Request(url, self.parse_book,meta={'id':idd})

    def parse_book(self, response):
        title = response.css('a.title::text').get()
        URL = response.url
        # print(URL)
        Genre = "-".join(response.css('div.info-detail__row a::text').getall())
        Genre = Genre.replace("-Learn more","")
        stats = response.css('div.stats a.stats__row::text').getall()
        Views_Count = (stats[0].strip().split(" ")[0])
        Views_Count=self.process(Views_Count)
        Subscribers_Count = (stats[1].strip().split(" ")[0])
        Subscribers_Count=self.process(Subscribers_Count)
        Likes_Count = (stats[2].strip().split(" ")[0])
        Likes_Count=self.process(Likes_Count)
        data = response.css(
            'ul.episode-list li:first-child div.info p.additional span::text').getall()
        Total_Number_of_Episodes = response.css(
            'p.episode-cnt::text').get().split(" ")[0]
        Total_Number_of_Episodes=self.process(Total_Number_of_Episodes)
        Plays_on_Episode_1 = data[1].split(" ")[0]
        Plays_on_Episode_1=self.process(Plays_on_Episode_1)
        Published_date_of_Episode_1 = data[0]
        Published_date_of_Episode_1=self.convert_date(Published_date_of_Episode_1)
        tags=response.css(".tags__item::text").getall()[:5]
        details=response.css("span.description__body::text").getall()[0]
        creator=response.css("a.name::text").getall()[0]
        self.output.append({
            "bookId": "tapas-comics-"+response.meta['id'],
            "Title Name": title,
            "URL": URL,
            "Genre": Genre,
            "Views Count": Views_Count,
            "Subscribers Count": Subscribers_Count,
            "Likes Count": Likes_Count,
            "Total Number of Episodes": Total_Number_of_Episodes,
            "Plays on Episode 1": Plays_on_Episode_1,
            "Published date of Episode 1": Published_date_of_Episode_1,
            "Tags": tags,
            "Details": details,
            "Creator": creator
        })

    def process(self,num):
        try:
            num=str(num)
            if num[-1]=='k':
                return int(float(num[:-1])*1000)
            elif num[-1]=='m':
                return int(float(num[:-1])*1000000)
            return int(num)
        except Exception as e:
            print(e)
            return "NA"
        
    def convert_date(self,date_str):
        input_format = "%b %d, %Y"
        # Parse the input date string into a datetime object
        date_obj = datetime.strptime(date_str, input_format)
        # Format the datetime object into the desired format
        output_format = "%Y-%m-%d"
        return date_obj.strftime(output_format)

    def closed(self, reason):
        df = pd.DataFrame(self.output)
        df.to_csv(f"tapas-comics-{self.genre}.csv", index=False)


def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    output_dict = {}

    process.crawl(TapasSpider)
    process.start()


if __name__ == "__main__":
    main()