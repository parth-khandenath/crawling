import scrapy
from scrapy.crawler import CrawlerProcess
from bs4 import BeautifulSoup
import pandas as pd
import re


class SeventeenKSpider(scrapy.Spider):
    name = "seventeenk"
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1,
        # 'Cookie':'GUID=a03ebd3f-9d62-4062-a757-f6123b8d0828; __root_domain_v=.4yt.net; _qddaz=QD.165103683998284; Hm_lvt_9ebbc52cb334f47110052681488d16f0=1703657826,1703683996,1704221291; acw_sc__v2=65945b12b82909c1927ec78e18bf061b4739eac4; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22a03ebd3f-9d62-4062-a757-f6123b8d0828%22%2C%22%24device_id%22%3A%2218ca9eb71192ab-06856b14af844c-26001951-1327104-18ca9eb711a77%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.google.com%2F%22%2C%22%24latest_referrer_host%22%3A%22www.google.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%7D; _qdda=3-1.10ga5x; _qddab=3-2t77f8.lqwpo5fj; lastSE=google; acw_tc=2760828817042231544621051e4ed94ba624b232f5d6c5f3d24565c81b79a8; acw_sc__v2=659461cab8540a0243f392032c1871b888431069; Hm_lpvt_9ebbc52cb334f47110052681488d16f0=1704223181; ssxmod_itna2=mq0x0D2DRi0=0QG8DzxAx=r=TaEzY5dWYYqD61bQD0vyq03qD9DHa08Dwjy0RLTTU1ZK4APzrIgqojGui0fEUY=I1myq43m4e93j0jK/0wU08+ARrP98cn7kh0whB3lYPwwz2UM2Q8G1YBYx6MQwfgi1Q+GxNb2LBo2+fD=qpCbMlwpxQYNcBhGtBfrvGo+x+RAYRqnc8j=dqrf38DISUd45yMiwmD6SYnAdiMFsa7RS78T+geEl/aXAgOtXtW=ChrhxBfBjkOIGCWAq9KnL+YAfZOdVBQ+S7vPkyxWsG80+zAtglx7emdFlDgQdsmQO0EijqVcoWaok0odc0SWmfEi+YmGWm9eesjrj13=RvzjKKa=Tbbeeh0AIuB2HRoKc0ZndInInCpTf5=Zjz86TaGylTFtu1DLsRjG2TnGte1NEGuY1mp2I+7nr8u006AU05nG9AGKnD4OomCj37Gs0A5AwF0d4zWS1bpj=uYAsgAFADKOPdK6O7iH0Yu1A8ldxs7/4rAoTb/h+bmYC4DQFDoGBFMtziy0p4DpFRCo9Cvo7zbFd8MI5c9Sl4QDHD2fvALgQDFqD+ODxD===; ssxmod_itna=QuDQYKiKBI8Hi=DXDnCmvK=pYGCtDjh8DqqGXwoGRDCqAPGwDebSpAi3EYxfDDvPvlabcGiv/=SWYqvFBj0ECVmDB3DEc8i4oaxeeDv+xGoDPxDeDADYEFDAkPD9D048y2pLKGWDbx=DaxDbDie82DGCDeKD0xD87x07DQy8PDDzPAoisxrYVrYFYUbmX=Dh5CD8D7ymDlPeUFD8Q/8jP75hvI8sveqDXZdDvoy3ycbmDBR8B=HsSi2ooihegmiaimRD5lw5WW0rWdRNmWDezebaqD2DzAnrM7btHWGDD===',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

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
        # soup = BeautifulSoup(response.text, 'lxml')
        # print(soup)
        # page_info = response.css('.page').getall()
        # # page_info=soup.select(".page font font")
        # print("#######")
        # print(page_info)
        # if page_info:
        #     page_text = page_info.strip()
        #     if '共' in page_text and '页' in page_text:
        #         last_pg = int(page_text.split("共")[1].split("页")[0].strip())
        last_pg=334
                
        for i in range(1, last_pg+1):
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

    def next_crawl(i):
        try:
            output_dict[names[i]] = []
            a = process.crawl(SeventeenKSpider, start_urls=links[i],
                            name=names[i], output_dict=output_dict)
            a.addCallback(lambda _: next_crawl(i + 1))
        except IndexError:
            # process.stop()
            pass

    next_crawl(0)
    process.start()

if __name__ == "__main__":
    main()
