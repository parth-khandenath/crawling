import scrapy
import docx
from bs4 import BeautifulSoup as bs
import time

import scrapy

class Shu69Spider(scrapy.Spider):
    name = "shu_69"
    allowed_domains = ["www.69shu.top"]
    start_urls = ['https://www.69shu.top/book/10060338.htm']
    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    def __init__(self, **kwargs):
        self.start_urls = ['https://www.69shu.top/book/10060338.htm']
        self.start = 1
        self.end = 20
        self.output_dict = "./"
        self.count = self.start - 1
        self.doc = docx.Document()
        self.priority = 100000000

    def start_requests(self):
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "accept-language": "en-US,en;q=0.7",
            # "cache-control": "max-age=0",
            "cookie": "zh_choose=s; g_session=c275d853c4c142130966fa0cc277b7b5; history_val2=1714977570@fca298ff60c4e8bb42a06c6b8f5796f5; zh_choose=s; shuba=9125-11332-20654-3505; g_action=1714974926@f5+uEn8w1MYkV64AsoMIhncTxMzXrHPrI8CdNTctmF9/VJVWckPpzwwtcOj9r9MWRJES4Ntw6A7qCO1VKrmHI6KiKGGgOGeNwPJ6WdWlJ5FocA==",
            # "if-modified-since": "Mon, 06 May 2024 05:54:38 GMT",
            # "if-none-match": "\"e255b24a125e0927eb9960e093240e9c\"",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Chromium\";v=\"124\", \"Brave\";v=\"124\", \"Not-A.Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "none",
            "sec-fetch-user": "?1",
            "sec-gpc": "1",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        }
        for url in self.start_urls:
            yield scrapy.Request(url=url.replace('.htm',''), headers=headers, callback=self.parse)

    def parse(self, response):
        print("#######################")
        print("here")
        print("#######################")