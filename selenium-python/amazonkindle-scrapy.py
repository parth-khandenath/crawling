from bs4 import BeautifulSoup
import scrapy
import json
import pandas as pd
from scrapy.crawler import CrawlerProcess

#per category 2 pages
#per page rendering patterns
#server - 30 books
#1st api call - 8 books
#2nd api call - 8 books
#3rd api call - 4 books

class AmazonListing(scrapy.Spider):
    name = "amazon_listing"
    allowed_domains = ["www.amazon.com"]

    def __init__(self, **kwargs):
        url=kwargs.get("start_urls", None)
        self.start_urls = []
        for i in range(1,3):
            self.start_urls.append(url+f'&pg={i}')
        self.book_name = kwargs.get("name", None)
        self.output_dict = kwargs["output_dict"]
        self.pg1stamp="1709119479077" #change here
        self.pg2stamp="1709119424413" #change here
        self.api_url="https://www.amazon.com/acp/p13n-zg-list-grid-desktop/p13n-zg-list-grid-desktop-23f2d9aa-79df-43ee-88f9-b7598ffd450e-1704992580789/nextPage?page-type=zeitgeist&stamp="  #change here
        # self.priority = 100000000
        # self.totalPagesCount = None
        self.category = kwargs.get("category", None)+"fantasy"
        self.excel_headers = {
            "Id": [],
            "Title": [],
            "URL": [],
            "Author + Profile Link": [],
            "Format": [],
            "Rating + No of Ratings": [],
            "Kindle Price": [],
            "Best Sellers Rank": [],
            "% of 4 and 5-star ratings(Combined)": [],
            "Print Length": [],
            "Language": [],
            "Publication Date": [],
            "Publisher": [],
            "Summary": [],
        }
        try:
            self.df=pd.read_csv(self.book_name+".csv")
        except:
            self.df=pd.DataFrame(self.excel_headers)

    custom_settings = {
        "CONCURRENT_REQUESTS": 1,
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "headers":{
            'authority': 'www.amazon.com',
            'accept': 'text/html, application/json',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'content-type': 'application/json',
            'cookie': 'aws-ubid-main=740-7370645-5242451; session-id=131-6894656-6125142; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:IN"; ubid-main=133-5129884-6918967; skin=noskin; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Asts%3A%3A856517911253%3Aassumed-role%2FAWSReservedSSO_BackInnies_fa60f0f6242afd57%2Fparth.khandenath%40pocketfm.com%22%2C%22alias%22%3A%22radio-ly%22%2C%22username%22%3A%22assumed-role%252FAWSReservedSSO_BackInnies_fa60f0f6242afd57%252Fparth.khandenath%2540pocketfm.com%22%2C%22keybase%22%3A%22vQ99v68c4K02OcaQJMYUnJGG6MnfhVcS7vmqgTLpszE%5Cu003d%22%2C%22issuer%22%3A%22https%3A%2F%2Fpocketfm-apsoutheast-1.awsapps.com%2Fstart%2F%23%2Fsaml%2Fcustom%2F856517911253%2520%2528Radio.ly%2529%2FODU2NTE3OTExMjUzX2lucy05N2JhZTU2YWQ0Mjc4OGNmX3AtMTY2NzEwZmYyZTdiYTJlNg%5Cu003d%5Cu003d%22%2C%22signinType%22%3A%22PUBLIC%22%7D; aws-userInfo-signed=eyJ0eXAiOiJKV1MiLCJrZXlSZWdpb24iOiJhcC1zb3V0aGVhc3QtMSIsImFsZyI6IkVTMzg0Iiwia2lkIjoiNzc2YjdlYTUtODRhYi00N2I0LTg1MmMtMjBhNDJjNjEwYjBlIn0.eyJzdWIiOiJyYWRpby1seSIsInNpZ25pblR5cGUiOiJQVUJMSUMiLCJpc3MiOiJodHRwczpcL1wvcG9ja2V0Zm0tYXBzb3V0aGVhc3QtMS5hd3NhcHBzLmNvbVwvc3RhcnRcLyNcL3NhbWxcL2N1c3RvbVwvODU2NTE3OTExMjUzJTIwJTI4UmFkaW8ubHklMjlcL09EVTJOVEUzT1RFeE1qVXpYMmx1Y3kwNU4ySmhaVFUyWVdRME1qYzRPR05tWDNBdE1UWTJOekV3Wm1ZeVpUZGlZVEpsTmc9PSIsImtleWJhc2UiOiJ2UTk5djY4YzRLMDJPY2FRSk1ZVW5KR0c2TW5maFZjUzd2bXFnVExwc3pFPSIsImFybiI6ImFybjphd3M6c3RzOjo4NTY1MTc5MTEyNTM6YXNzdW1lZC1yb2xlXC9BV1NSZXNlcnZlZFNTT19CYWNrSW5uaWVzX2ZhNjBmMGY2MjQyYWZkNTdcL3BhcnRoLmtoYW5kZW5hdGhAcG9ja2V0Zm0uY29tIiwidXNlcm5hbWUiOiJhc3N1bWVkLXJvbGUlMkZBV1NSZXNlcnZlZFNTT19CYWNrSW5uaWVzX2ZhNjBmMGY2MjQyYWZkNTclMkZwYXJ0aC5raGFuZGVuYXRoJTQwcG9ja2V0Zm0uY29tIn0.IafD94OK7MsDzBgB0hmZhM0lQx5O1qz2PYkf-5lCLhysfZ4uW5Y3GBp6w50FNX9C5POzNNed4lIduH0S64YlUfIGsVIY1ytpqckFj41Ba-3n2YLA7ZhX9wZkzQ1-Ecek; noflush_awsccs_sid=bb5b846d0805b435693bebe569b4f935c25378d840435f35351e727e04b7e582; aws-signer-token_ap-southeast-1=eyJrZXlWZXJzaW9uIjoiTHVuMUllLnFTQVJ5R3hUVnVld2NRQ3E5WTIyVUU5dWwiLCJ2YWx1ZSI6Ikt3aDBOQWJIRWIzQ0RIMmQzbVBmMlF4cTZ1OEdadjBYTVRDbzBzcUM2dEU9IiwidmVyc2lvbiI6MX0=; lc-main=en_US; session-token=xwQmSvXNDPJVWez+hDHA2OtfxGQgYsmXFz5hdQcMRDNQwzOLCqSJh0tttG9pvqOnV0elJhkZnqC5qS5agW/byfG9ZdV1K5PpjNKVs97LNzNNpnJTLYg2e4/b8bYhclN6bfLXNk/8PJAk6CjI4DziDrQ7CHiHBK3cxj6gGpc7qQo3kV1Fcy2Mkg+PMwTQGC7a1+MIZUbxFgs2uZM0wiGSC+HS8A5LUv74XbXwvSquj4Emv+Z1OVaRm0TNzfGyeo2Tp5QZBPg5uhvZRosKfM+jUASFxjQBt4SoQtJePRH/+XR93xSWo0WQOW6TttMtyOKOcmypannYrGDgBnq4xQnJwSEQdy6ASe6G; csm-hit=tb:s-2EPE7G19EMPJ4CEECS0A|1709116492730&t:1709116493098&adb:adblk_no; session-token=E9S33kqcxU4BJq5WRvIr7312/hIul5+aDI5AIf47H17FfDJbeBS284qOsGCBbPrgcOruVF2SMLK0AHiErMFwW1yBudltxEbhTEgWo+zWDmnSZ+h/GtHw3cnz50s1z8UWTqiUDVqJ61QWLLX/32RCkaEAmemI+zByIvqQ3s1iVxwIlhEmXrLO/fX5qY1G1j+s1hYi1e4WleS15RrS4regXpU7NK/A2QjRJ6GMx/jzey4TtP/Yl7E2ZXZJ7xMG8LdqkwPwWkW2W6YBQA/O7rSul4dCHpGXiVZlkge3PPRHI9MhFXyiXrgJdbnk6SoIvMjRmziPitb2UjSWdxKUnLqrG3Nd7n4Grtt7',
            'device-memory': '8',
            'downlink': '3.85',
            'dpr': '1.25',
            'ect': '4g',
            'origin': 'https://www.amazon.com',
            'referer': 'https://www.amazon.com/Best-Sellers-Kindle-Store-Science-Fiction/zgbs/digital-text/158591011/ref=zg_bs_pg_2_digital-text?_encoding=UTF8&pg=2',
            'rtt': '200',
            'sec-ch-device-memory': '8',
            'sec-ch-dpr': '1.25',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-ch-ua-platform-version': '"15.0.0"',
            'sec-ch-viewport-width': '1111',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'viewport-width': '1111',
            'x-amz-acp-params': 'tok=KrK7Tn_0Pz5-BQmsE33BFslD-pq8nFLOfgdMUFqaV4E;ts=1709116492424;rid=2EPE7G19EMPJ4CEECS0A;d1=142;d2=0',
            'x-requested-with': 'XMLHttpRequest'
        }
    }

    def start_requests(self):
        priority = 10000000000
        for i in range(2):
            yield scrapy.Request(
                self.start_urls[i],
                callback=self.parse,
                meta={"page":i+1}
                # priority=priority- i*5000000000,
            )

    def parse(self, response):
        page=response.meta["page"]
        book_eles=response.css("div.p13n-sc-uncoverable-faceout") #.getall()
        ranks=response.css("span.zg-bdg-text::text").getall()
        i=0
        for ele in book_eles:
            book_name=ele.css(".a-link-normal ._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y::text").get()
            author=ele.css(".a-link-child ._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y::text").get()
            author_link="https://www.amazon.com" + ele.css(".a-link-child::attr(href)").get()
            book_link="https://www.amazon.com" + ele.css(".a-link-normal::attr(href)").get()
            book_id= book_link.split('/')[-3]
            rating=ele.css(".a-icon-row .a-link-normal::attr(title)").get()
            num_of_ratings= ele.css("span.a-size-small::text").get()
            format=ele.css("span.a-text-normal::text").get()
            price=ele.css("span._cDEzb_p13n-sc-price_3mJ9Z::text").get()
            rank=ranks[i] #ele.css("span.zg-bdg-text::text").get()
            i+=1

            data={
                    "book_name":book_name,
                    "author":author,
                    "author_link":author_link,
                    "book_link":book_link,
                    "book_id":book_id,
                    "rating":rating,
                    "num_of_ratings":num_of_ratings,
                    "format":format,
                    "price":price,
                    "rank":rank
                }
            # print(data)
            yield scrapy.Request(
                url=book_link,
                callback=self.parse_book,
                meta=data
                # priority=1,
            )

        #change payloads
        payloads=[json.dumps({
                "faceoutkataname": "GeneralFaceout",
                "ids": [
                    "{\"id\":\"B07B6BRTJP\",\"metadataMap\":{\"render.zg.rank\":\"31\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B09W2BLL4B\",\"metadataMap\":{\"render.zg.rank\":\"32\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CTKS5LHD\",\"metadataMap\":{\"render.zg.rank\":\"33\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B000FBJCJE\",\"metadataMap\":{\"render.zg.rank\":\"34\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CV3Y9BSB\",\"metadataMap\":{\"render.zg.rank\":\"35\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CSCB1D3B\",\"metadataMap\":{\"render.zg.rank\":\"36\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CLQF6RQ4\",\"metadataMap\":{\"render.zg.rank\":\"37\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0011UGNDG\",\"metadataMap\":{\"render.zg.rank\":\"38\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}"
                ],
                "indexes": [
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37
                ],
                "linkparameters": "",
                "offset": "30",
                "reftagprefix": "zg_bs_g_158591011"
                }), 
                json.dumps({
                "faceoutkataname": "GeneralFaceout",
                "ids": [
                    "{\"id\":\"B08FHBV4ZX\",\"metadataMap\":{\"render.zg.rank\":\"39\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CRGML5VV\",\"metadataMap\":{\"render.zg.rank\":\"40\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B000FC1PWA\",\"metadataMap\":{\"render.zg.rank\":\"41\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CST48F1H\",\"metadataMap\":{\"render.zg.rank\":\"42\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0C4LH9ST5\",\"metadataMap\":{\"render.zg.rank\":\"43\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CRS84W36\",\"metadataMap\":{\"render.zg.rank\":\"44\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B07N32K12H\",\"metadataMap\":{\"render.zg.rank\":\"45\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0BSV7ZF68\",\"metadataMap\":{\"render.zg.rank\":\"46\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}"
                ],
                "indexes": [
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45
                ],
                "linkparameters": "",
                "offset": "38",
                "reftagprefix": "zg_bs_g_158591011"
                }),
                json.dumps({
                "faceoutkataname": "GeneralFaceout",
                "ids": [
                    "{\"id\":\"B0CR99GBQB\",\"metadataMap\":{\"render.zg.rank\":\"47\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B014LZK0LS\",\"metadataMap\":{\"render.zg.rank\":\"48\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B003JFJHTS\",\"metadataMap\":{\"render.zg.rank\":\"49\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B09XL7N9XD\",\"metadataMap\":{\"render.zg.rank\":\"50\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}"
                ],
                "indexes": [
                    46,
                    47,
                    48,
                    49
                ],
                "linkparameters": "",
                "offset": "46",
                "reftagprefix": "zg_bs_g_158591011"
                }),
                json.dumps({
                "faceoutkataname": "GeneralFaceout",
                "ids": [
                    "{\"id\":\"B0CR9B91VN\",\"metadataMap\":{\"render.zg.rank\":\"81\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B088H926KF\",\"metadataMap\":{\"render.zg.rank\":\"82\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CJT8JTBP\",\"metadataMap\":{\"render.zg.rank\":\"83\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B017KRJ1UK\",\"metadataMap\":{\"render.zg.rank\":\"84\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0050DEY54\",\"metadataMap\":{\"render.zg.rank\":\"85\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B09T6Z5DXT\",\"metadataMap\":{\"render.zg.rank\":\"86\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0848VHFRR\",\"metadataMap\":{\"render.zg.rank\":\"87\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CK7M5QW9\",\"metadataMap\":{\"render.zg.rank\":\"88\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}"
                ],
                "indexes": [
                    30,
                    31,
                    32,
                    33,
                    34,
                    35,
                    36,
                    37
                ],
                "linkparameters": "",
                "offset": "30",
                "reftagprefix": "zg_bs_g_158591011"
                }),
                json.dumps({
                "faceoutkataname": "GeneralFaceout",
                "ids": [
                    "{\"id\":\"B0C2J6Z786\",\"metadataMap\":{\"render.zg.rank\":\"89\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B082SCZ2WV\",\"metadataMap\":{\"render.zg.rank\":\"90\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0C2QP39F5\",\"metadataMap\":{\"render.zg.rank\":\"91\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CK46BC1S\",\"metadataMap\":{\"render.zg.rank\":\"92\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B08HRQ44JJ\",\"metadataMap\":{\"render.zg.rank\":\"93\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B01DGXSHRK\",\"metadataMap\":{\"render.zg.rank\":\"94\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CM76YYN5\",\"metadataMap\":{\"render.zg.rank\":\"95\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                    "{\"id\":\"B0CMKGMWHP\",\"metadataMap\":{\"render.zg.rank\":\"96\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}"
                ],
                "indexes": [
                    38,
                    39,
                    40,
                    41,
                    42,
                    43,
                    44,
                    45
                ],
                "linkparameters": "",
                "offset": "38",
                "reftagprefix": "zg_bs_g_158591011"
                }),
                json.dumps({
                    "faceoutkataname": "GeneralFaceout",
                    "ids": [
                        "{\"id\":\"B08HKW7X8Y\",\"metadataMap\":{\"render.zg.rank\":\"97\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                        "{\"id\":\"B0BVL2C8ZQ\",\"metadataMap\":{\"render.zg.rank\":\"98\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                        "{\"id\":\"B07P92TDXQ\",\"metadataMap\":{\"render.zg.rank\":\"99\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}",
                        "{\"id\":\"B018ER7IPK\",\"metadataMap\":{\"render.zg.rank\":\"100\",\"render.zg.bsms.currentSalesRank\":\"\",\"render.zg.bsms.percentageChange\":\"\",\"render.zg.bsms.twentyFourHourOldSalesRank\":\"\",\"disablePercolateLinkParams\":\"true\"},\"linkParameters\":{}}"
                    ],
                    "indexes": [
                        46,
                        47,
                        48,
                        49
                    ],
                    "linkparameters": "",
                    "offset": "46",
                    "reftagprefix": "zg_bs_g_158591011"
                    })
                ]
        if page==1:
            stmp=self.pg1stamp
        elif page==2:
            stmp=self.pg2stamp
        for i in range(3):
            print(f"page:{page}, api call:{i+1}")
            yield scrapy.FormRequest(url=self.api_url+stmp,callback=self.parse2,meta={**data,"page": page},formdata=payloads[3*(page-1)+i])   

    def parse2(self,response):
        soup = BeautifulSoup(response.text, 'lxml')
        book_eles = soup.select("div.p13n-sc-uncoverable-faceout")
        ranks = soup.select("span.zg-bdg-text")

        for i, ele in enumerate(book_eles):
            book_name = ele.select_one(".a-link-normal ._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y").get_text(strip=True)
            author = ele.select_one(".a-link-child ._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y").get_text(strip=True)
            author_link = "https://www.amazon.com" + ele.select_one(".a-link-child")["href"]
            book_link = "https://www.amazon.com" + ele.select_one(".a-link-normal")["href"]
            book_id = book_link.split('/')[-3]
            rating = ele.select_one(".a-icon-row .a-link-normal")["title"] if ele.select_one(".a-icon-row .a-link-normal") else None
            num_of_ratings = ele.select_one("span.a-size-small").get_text(strip=True) if ele.select_one("span.a-size-small") else None
            format = ele.select_one("span.a-text-normal").get_text(strip=True) if ele.select_one("span.a-text-normal") else None
            price = ele.select_one("span._cDEzb_p13n-sc-price_3mJ9Z").get_text(strip=True) if ele.select_one("span._cDEzb_p13n-sc-price_3mJ9Z") else None
            rank = ranks[i].get_text(strip=True) if i < len(ranks) else None

            data = {
                "book_name": book_name,
                "author": author,
                "author_link": author_link,
                "book_link": book_link,
                "book_id": book_id,
                "rating": rating,
                "num_of_ratings": num_of_ratings,
                "format": format,
                "price": price,
                "rank": rank
            }

            yield scrapy.Request(
                url=book_link,
                callback=self.parse_book,
                meta=data
            )


    def parse_book(self,response):
        meta=response.meta
        percents=response.css("#histogramTable .a-text-right .a-size-base::text").getall()
        percent5star=int(percents[0][:-1])
        percent4star=int(percents[1][:-1])
        percent_4n5stars=f"{str(percent5star+percent4star)}%"
        print_length=response.css("li:nth-child(13) .a-text-bold+ span::text").get()
        lang=response.css("li:nth-child(4) .a-text-bold+ span::text").get()
        pub_date=response.css("li:nth-child(3) .a-text-bold+ span::text").get()
        publisher=response.css("li:nth-child(2) .a-text-bold+ span::text").get()
        summary=response.css(".a-expander-content-expanded span::text").get()

        self.df.loc[len(self.df.index)]=[meta["book_id"],meta['book_name'],meta['book_link'],str(meta['author'])+'+'+str(meta['author_link']),meta['format'],str(meta['rating'])+'+'+str(meta['num_of_ratings']),meta['price'],meta['rank'],percent_4n5stars,print_length,lang,pub_date,publisher,summary]
        self.df.to_csv(self.book_name+".csv",index=False)


    def closed(self, reason):
         pass


def main():
    process = CrawlerProcess(
        {
            "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
    )

    
    urls = [
        "https://www.amazon.com/Best-Sellers-Kindle-Store-Fantasy/zgbs/digital-text/158576011/ref=zg_bs_pg_1_digital-text?_encoding=UTF8",
        # "https://www.amazon.com/gp/bestsellers/digital-text/158576011/ref=zg_bs_pg_1_digital-text?ie=UTF8&tf=1",
        # "https://www.amazon.com/Best-Sellers-Kindle-Store-Science-Fiction/zgbs/digital-text/158591011/ref=zg_bs_pg_1_digital-text?_encoding=UTF8",
        # "https://www.amazon.com/gp/bestsellers/digital-text/158591011/ref=zg_bs_pg_1_digital-text?ie=UTF8&tf=1"
    ]
 
    names = [
        "Fantasy Top 100 Paid",
        # "Fantasy Top 100 Free",
        # "SciFi Top 100 Paid",
        # "SciFi Top 100 Free"
    ]

    output_dict = {}

    def next_crawl(i):
        try:
            output_dict[names[i]] = []
            a = process.crawl(
                AmazonListing,
                start_urls=urls[i],
                name=names[i],
                category=names[i].split("-")[1],
                output_dict=output_dict,
            )
            a.addCallback(lambda _: next_crawl(i + 1))
        except IndexError:
            pass

    next_crawl(0)
    process.start()


if __name__ == "__main__":
    main()