import scrapy
import xml.etree.ElementTree as ET
import pandas as pd
from scrapy.crawler import CrawlerProcess
import json
import bs4


class TapasSpider(scrapy.Spider):
    name = 'tapas_spider'
    output = []
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1000,
    }

    def start_requests(self):

        for i in range(1, 1300):

            url = f"https://tapas.io/novels?b=ALL&g=0&f=NONE&s=SUBSCRIBE&pageNumber={i}&pageSize=20"

            yield scrapy.Request(url, self.parse)

    def parse(self, response, **kwargs):

        urls = response.css('a.row-item::attr(href)').getall()

        for i in urls:
            url = "https://tapas.io" + i + "/info"
            yield scrapy.Request(url, self.parse_book)

    def parse_book(self, response):
        title = response.css('a.title::text').get()
        URL = response.url
        Genre = "-".join(response.css('div.info-detail__row a::text').getall())
        stats = response.css('div.stats a.stats__row::text').getall()
        Views_Count = stats[0].strip().split(" ")[0]
        Subscribers_Count = stats[1].strip().split(" ")[0]
        Likes_Count = stats[2].strip().split(" ")[0]
        data = response.css(
            'ul.episode-list li:first-child div.info p.additional span::text').getall()
        Total_Number_of_Episodes = response.css(
            'p.episode-cnt::text').get().split(" ")[0]
        Plays_on_Episode_1 = data[1].split(" ")[0]
        Published_date_of_Episode_1 = data[0]
        tags=response.css(".tags__item::text").getall()[:5]
        details=response.css("span.description__body::text").getall()[0]
        creator=response.css("a.name::text").getall()[0]
        self.output.append({
            "Title Name": title,
            "URL": URL,
            "Genre": Genre,
            "Views Count": Views_Count,
            "Subscribers Count": Subscribers_Count,
            "Likes Count": Likes_Count,
            "Total Number of Episodes": Total_Number_of_Episodes,
            # "Plays on Episode 1": Plays_on_Episode_1,
            "Published date of Episode 1": Published_date_of_Episode_1,
            "Tags": tags,
            "Details": details,
            "Creator": creator
        })

    def closed(self, reason):
        df = pd.DataFrame(self.output)
        df.to_csv(f"tapas.csv", index=False)


def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    output_dict = {}

    process.crawl(TapasSpider)
    process.start()


if __name__ == "__main__":
    main()