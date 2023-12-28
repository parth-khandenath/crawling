import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import pandas as pd
import re


class SeventeenKSpider(scrapy.Spider):
    name = "seventeenk"
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 100,
    }

    def __init__(self, **kwargs):
        self.start_urls = kwargs.get('start_urls', None)
        self.book_name = kwargs.get('name', None)
        self.output_dict = kwargs['output_dict']
        self.priority = 1000000
        self.output = []

    def start_requests(self):

        url1 = self.start_urls+"_1.html"

        yield scrapy.Request(url=url1, callback=self.parse1)

    def parse1(self, response):
        text = response.css('div.page').get()
        text = int(text.split("共")[1].split("页")[0].strip())
        for i in range(1, text+1):
            url = self.start_urls + \
                f"_{i}.html"
            yield scrapy.Request(url=url, callback=self.parse, priority=i, dont_filter=True)
            yield scrapy.Request(url=url, callback=self.parse, priority=-i, dont_filter=True)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'lxml')
        trs = soup.select("tr")[2:]

        for tr in trs:
            title = tr.select_one("a.jt").get_text(strip=True)
            book_url = tr.select_one("a.jt")["href"]
            book_url = f"http:{book_url}"
            category = tr.select_one("td.td2").get_text(strip=True)
            category = tr.select_one("td.td2 a").get_text(strip=True)
            latest_chapter = tr.select_one("td.td4").get_text(strip=True)
            update_time = tr.select_one("td.td7").get_text(strip=True)
            author = tr.select_one("td.td6").get_text(strip=True)
            state = tr.select_one("td.td8").get_text(strip=True)

            yield scrapy.Request(
                url=book_url,
                callback=self.parse_book_details,
                meta={
                    "title": title,
                    "category": category,
                    "latest_chapter": latest_chapter,
                    "update_time": update_time,
                    "author": author,
                    "state": state,
                    "book_url": book_url
                }
            )

    def parse_book_details(self, response):
        # readers = soup1.find('em', {'id': 'howmuchreadBook'}).text.strip()
        readers = response.css('em#howmuchreadBook::text').get()
        words = response.css('em.red::text').get()
        book_details_url = response.css('dt.read a::attr(href)').get()
        book_details_url = f"https://www.17k.com{book_details_url}"

        monthly_recomendations = response.css('td#flower_month::text').get()

        tags = "-".join(response.css('tr.label td a span::text').getall())

        yield scrapy.Request(
            url=book_details_url,
            callback=self.parse_detailed_book_details,
            meta={
                **response.meta,
                "readers": readers,
                "words": words,
                "monthly_recomendations": monthly_recomendations,
                "tags": tags
            }
        )

    def parse_detailed_book_details(self, response):

        dls = response.css('dl.Volume')
        num_chapters = 0
        for dl in dls:
            num_chapters += len(dl.css('span.ellipsis'))

        pattern = '^\d+'
        for part in response.meta['book_url'].split('/')[::-1]:
            if part!='':
                match = re.match(pattern, part)
                if match:
                    bookId=match[0]
                    break

        object = {
            "title": response.meta["title"],
            "category": response.meta["category"],
            "book_id":bookId,
            "latest_chapter": response.meta["latest_chapter"],
            "update_time": response.meta["update_time"][:10],
            "author": response.meta["author"],
            "status": response.meta["state"],
            "URL": response.meta["book_url"],
            "tags": response.meta["tags"],
            "Number of Readers":  response.meta["readers"],
            "Number of Chapters": num_chapters,
            "Number of Words":  response.meta["words"],
            "Total Monthly Recommendation": response.meta["monthly_recomendations"]
        }

        self.output.append(object)

    def closed(self, reason):
        self.output_dict[self.name] = self.output
        df = pd.DataFrame(self.output)
        df.to_csv(f"17k-out/{self.book_name}.csv", index=False)


def main():
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    })

    links = [
        "https://www.17k.com/all/book/2_0_0_0_0_4_0_0",
        "https://www.17k.com/all/book/3_0_0_0_0_4_0_0",
    ]

    names = [
        "17k - Total Clicks Male",
        "17k - Total Clicks Female"
    ]
    output_dict = {}

    for i in range(len(links)):
        output_dict[names[i]] = []
        process.crawl(SeventeenKSpider, start_urls=links[i],
                      name=names[i], output_dict=output_dict)

    process.start()


if __name__ == "__main__":
    main()
