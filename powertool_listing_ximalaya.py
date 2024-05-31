import scrapy
import json
import html2text
import pandas as pd
from scrapy.crawler import CrawlerProcess


class PowertoolListingXimalaya(scrapy.Spider):
    name = "listing_Ximalaya"
    allowed_domains = ["www.ximalaya.com"]

    def __init__(self, **kwargs):
        self.start_urls = [kwargs.get("start_urls", None)]
        self.book_name = kwargs.get("name", None)
        self.output_dict = kwargs["output_dict"]
        self.priority = 100000000
        self.globalPagesCount = 50
        self.excel_headers = {
            "AlbumId": [],
            "Title name": [],
            "Plays": [],
            "URL": [],
            "Introduction": [],
            "Number of tracks": [],
            "Plays of first chapter": [],
            "Date of first chapter": [],
            "vip status": [],
        }

    custom_settings = {
        "CONCURRENT_REQUESTS": 100,
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
    }

    headers = {
        "authority": "www.ximalaya.com",
        "accept": "*/*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "cookie": "_xmLog=h5&630426cb-3ac8-4be5-bc43-2c171ac91f50&process.env.sdkVersion; Hm_lvt_4a7d8ec50cfd6af753c4f8aee3425070=1683016301; hide_himayala_bar=1; fds_otp=6222371113542586084; 1&remember_me=y; 1&_token=468425582&46FC7E60340NBC7334D34DF1C9B318AC0E42752F064776BB53D449D2B2B7389ED643330BE3B246MEE9155929A4647B_; login_type=code_mobile; xm-page-viewid=ximalaya-web; impl=www.ximalaya.com.login; x_xmly_traffic=utm_source%253A%2526utm_medium%253A%2526utm_campaign%253A%2526utm_content%253A%2526utm_term%253A%2526utm_from%253A; web_login=1683027908148",
        "referer": "https://www.ximalaya.com/album/4756811",
        "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
        "xm-sign": "c03b9c71357310f0749d58ee60dd1343(75)1683027931132(76)1683027909330",
    }

    def parse(self, response):
        priority = 10000000000

        if not response.text:
            self.logger.warning(f"Skipping {response.url} as no data is being returned")
            return

        pagesCount = self.globalPagesCount

        for i in range(pagesCount):
            url = (
                f"https://www.ximalaya.com/revision/category/v2/albums?pageNum={i + 1}"
                + response.url[62:]
            )
            yield scrapy.Request(
                url=url,
                callback=self.parse_album,
                meta={
                    "current_priority": priority,
                },
                headers=self.headers,
                priority=priority,
            )
            priority -= 10000

    def parse_album(self, response):
        data = json.loads(response.text)
        current_priority = response.meta.get("current_priority")

        for da in data["data"]["albums"]:
            album_id = da["albumId"]
            album_title = da["albumTitle"]
            album_plays = da["albumPlayCount"]
            vip_status = da["isPaid"]
            album_url = f"https://www.ximalaya.com/album/{album_id}"
            author_url = (
                f"https://www.ximalaya.com/revision/album/v1/simple?albumId={album_id}"
            )
            track_url = f"https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum=1&pageSize=30"

            current_priority -= 10
            yield scrapy.Request(
                url=author_url,
                callback=self.parse_author,
                meta={
                    "album_id": album_id,
                    "album_title": album_title,
                    "album_plays": album_plays,
                    "album_url": album_url,
                    "track_url": track_url,
                    "vip_status": vip_status,
                    "current_priority": current_priority,
                },
                priority=current_priority,
            )

    def parse_author(self, response):
        data = response.meta
        data_author = json.loads(response.text)
        try:
            intr = data_author["data"]["albumPageMainInfo"]["detailRichIntro"]
            intro = html2text.html2text(intr)
        except:
            intro = "N/A"

        yield scrapy.Request(
            url=data["track_url"],
            callback=self.parse_tracks,
            meta={**data, "intro": intro, "p": data["current_priority"] - 2},
            priority=data["current_priority"] - 2,
        )

    def parse_tracks(self, response):
        data = response.meta
        data_tracks = json.loads(response.text)

        number_of_tracks = data_tracks["data"]["trackTotalCount"]
        first_chapter_plays = data_tracks["data"]["tracks"][0]["playCount"]
        first_chapter_date = data_tracks["data"]["tracks"][0]["createDateFormat"]

        self.excel_headers["AlbumId"].append(data["album_id"])
        self.excel_headers["Title name"].append(data["album_title"])
        self.excel_headers["Plays"].append(data["album_plays"])
        self.excel_headers["URL"].append(data["album_url"])
        self.excel_headers["Introduction"].append(data["intro"])
        self.excel_headers["Number of tracks"].append(number_of_tracks)
        self.excel_headers["Plays of first chapter"].append(first_chapter_plays)
        self.excel_headers["Date of first chapter"].append(first_chapter_date)
        self.excel_headers["vip status"].append(data["vip_status"])

    def closed(self, reason):
        ans = pd.DataFrame(self.excel_headers)
        self.output_dict[f"ximalaya_{self.book_name}"] = ans


def main(output_dict):
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    )

    links = [
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E7%94%B7%E9%A2%91%E5%B0%8F%E8%AF%B4,%E5%A5%87%E5%B9%BB",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E7%94%B7%E9%A2%91%E5%B0%8F%E8%AF%B4,%E6%82%AC%E7%96%91%E7%81%B5%E5%BC%82",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E7%94%B7%E9%A2%91%E5%B0%8F%E8%AF%B4,%E9%83%BD%E5%B8%82",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E7%94%B7%E9%A2%91%E5%B0%8F%E8%AF%B4,%E4%BB%99%E4%BE%A0",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E7%94%B7%E9%A2%91%E5%B0%8F%E8%AF%B4,%E7%8E%84%E5%B9%BB",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E7%94%B7%E9%A2%91%E5%B0%8F%E8%AF%B4,%E5%8E%86%E5%8F%B2%E5%B0%8F%E8%AF%B4",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E7%94%B7%E9%A2%91%E5%B0%8F%E8%AF%B4,%E6%B8%B8%E6%88%8F%E5%B0%8F%E8%AF%B4",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E7%94%B7%E9%A2%91%E5%B0%8F%E8%AF%B4,%E7%A7%91%E5%B9%BB",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E5%A5%B3%E9%A2%91%E5%B0%8F%E8%AF%B4,%E5%B9%BB%E6%83%B3%E8%A8%80%E6%83%85",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E5%A5%B3%E9%A2%91%E5%B0%8F%E8%AF%B4,%E6%B5%AA%E6%BC%AB%E9%9D%92%E6%98%A5",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E5%A5%B3%E9%A2%91%E5%B0%8F%E8%AF%B4,%E7%8E%B0%E4%BB%A3%E8%A8%80%E6%83%85",
        "https://www.ximalaya.com/revision/category/v2/albums?pageNum=1&pageSize=56&sort=3&categoryId=3&metadataValues=%E5%A5%B3%E9%A2%91%E5%B0%8F%E8%AF%B4,%E5%8F%A4%E9%A3%8E%E8%A8%80%E6%83%85",
    ]

    names = [
        "General_Fantasy",
        "Suspense_Supernatural",
        "City",
        "Xian_Xia_(Cultivation)",
        "Traditional_Fantasy",
        "Historical_Fiction",
        "Game_Novel",
        "Sci_Fi",
        "Fantasy_Romance",
        "Teen_Romance",
        "Urban_Romance",
        "Teen_Romance",
    ]

    def next_crawl(i):
        try:
            a = process.crawl(
                PowertoolListingXimalaya,
                start_urls=links[i],
                name=names[i],
                output_dict=output_dict,
            )
            a.addCallback(lambda _: next_crawl(i + 1))

        except IndexError:
            # process.stop()
            pass

    next_crawl(0)
    process.start()
    import sys

    del sys.modules["twisted.internet.reactor"]
    from twisted.internet import reactor
    from twisted.internet import default

    default.install()


if __name__ == "__main__":
    output_dict = {"output": None}
    main(output_dict)
