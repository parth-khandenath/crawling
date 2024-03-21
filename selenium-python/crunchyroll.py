import random
import time
import requests
import scrapy
import json
import pandas as pd
from scrapy.crawler import CrawlerProcess


class CrunchyrollListing(scrapy.Spider):
    name = "crunchyroll_listing_8th_feb_2024_1"
    allowed_domains = ["www.crunchyroll.com", "crunchyroll.com"]

    def __init__(self, **kwargs):
        self.output_dict = kwargs["output_dict"]
        self.priority = 100000000
        self.currentPage = 0  # Start from page 1
        self.eachPage = 700  # Each page has 50 items
        self.start_urls = kwargs.get("start_urls", None)
        self.totalRecords = None
        self.totalPages = None  # Initialize totalPages
        self.pagesToGo = 300  # Number of pages to scrape``
        self.requestCount = 0
        self.headers = {
            'authority': 'www.crunchyroll.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InRhU1JqVlhnOXZiQ2Vlb0VyZk4zV1EiLCJ0eXAiOiJKV1QifQ.eyJhbm9ueW1vdXNfaWQiOiI0M2E4MDRiNy1kZTZlLTRjMGEtYjYzZS00MTcxYWU2MWFkOWEiLCJjbGllbnRfaWQiOiJjcl93ZWIiLCJjbGllbnRfdGFnIjoiKiIsImNvdW50cnkiOiJJTiIsImV4cCI6MTcxMDkzNzgxMiwianRpIjoiZjQwN2UwY2EtZDRlOC00N2E0LThmY2YtNzU3NjJjODI4M2RmIiwibWF0dXJpdHkiOiJNMiIsIm9hdXRoX3Njb3BlcyI6ImFjY291bnQgY29udGVudCBvZmZsaW5lX2FjY2VzcyIsInN0YXR1cyI6IkFOT05ZTU9VUyIsInRudCI6ImNyIn0.OigHV2Ljvn9erdAHb1EYOWsnO4BG-8x8KvKFYm3jMh_IpHim2nnk-BbCYNdao2_Z_wA52mc1r3eEJNG7UcNiiAGpPouAYXXvxPdUEiPNnv5UftVNyNzjJxpMV7QyjbmpFJW96idXX6xwogwyNVTa4xl7Z_V_tDjDysXzq8LhwCT5Assg0lZ15q8JJHiuuQZvrxGxWySX2e3YHEQ_TtR3tjj-alBorBXfUCq2KU1O1_oVH6iiLnozQXtVqOb71YJ5WJB47xuYn5slnFYEHOTrlMeaMSLnv1cduND0fXp9isRxo1QJA4fagDKrHnGV7biFolphpI8TPcDpj4RVy9L3ag',
            'referer': 'https://www.crunchyroll.com/series/GYE5X75GR/11eyes',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }


        # Set concurrency to 1 to avoid getting blocked
        self.custom_settings = {
            'CONCURRENT_REQUESTS': 1,
            'CONCURRENT_REQUESTS_PER_DOMAIN': 1,
            'CONCURRENT_REQUESTS_PER_IP': 1
        }

    def start_requests(self):
        url = self.start_urls[0].format(self.currentPage, self.eachPage)
        yield scrapy.Request(
            url=url,
            callback=self.parse,
            priority=self.priority,
            headers=self.headers
        )

    def parse(self, response):
        if not response.text:
            self.logger.warning(f"Skipping {response.url} as no data is being returned")
            return

        jsonResponse = json.loads(response.text)

        if "total" not in jsonResponse:
            self.logger.error(f"Total records not found in response: {jsonResponse}")
            return

        if self.totalRecords is None:
            self.totalRecords = jsonResponse["total"]

        if self.totalPages is None:
            self.totalPages = int(jsonResponse["total"] / self.eachPage)

        data = jsonResponse["data"]
    
        for item in data:
            id = item.get('id', '')
            title = item.get('title', '')
            url = f"https://www.crunchyroll.com/series/{item.get('id')}"
            rating = item.get('rating', {}).get('average', '')
            total_ratings = item.get('rating', {}).get('total', '')
            five_star_percentage = (item['rating'].get('5s', {}).get('percentage', 0) +
                                    item['rating'].get('4s', {}).get('percentage', 0))
            total_episodes = item.get('series_metadata', {}).get('episode_count', '')
            introduction = item.get('description', '')
            tags = ', '.join(item.get('series_metadata', {}).get('tenant_categories', []))
            audio_locales = ', '.join(item.get('series_metadata', {}).get('audio_locales', []))

            self.output_dict["Id"].append(id)
            self.output_dict["URL"].append(url)
            self.output_dict["Title"].append(title)
            self.output_dict["Rating"].append(rating)
            self.output_dict["Total Ratings"].append(total_ratings)
            self.output_dict["% of 5-star+4-star Reviews"].append(five_star_percentage)
            self.output_dict["Episode Count"].append(total_episodes)
            self.output_dict["Introduction"].append(introduction)
            self.output_dict["Tags"].append(tags)

            self.output_dict["Audio for Education Purpose"].append(audio_locales)

            review_data_url = f"https://www.crunchyroll.com/content-reviews/v2/en-US/review/series/{id}/list?page=1&page_size=5&sort=helpful"

            sleepTime = random.randint(5, 10)
            print(f"Sleeping for {sleepTime} seconds before fetching review data for {id}")
            time.sleep(sleepTime)
            total_reviews = self.get_review_count(review_data_url)
            print(f"Total Reviews for {id} : {total_reviews}")

            published_data_url = f"https://www.crunchyroll.com/content/v2/cms/series/{id}?locale=en-US"

            # print(f"Sleeping for {sleepTime} seconds before fetching published data for {id}")
            # time.sleep(sleepTime)
            # publisher = self.get_published_data(published_data_url)
            # print(f"Published Data for {id} : {publisher}")

            self.output_dict["Publisher"].append("")

            self.output_dict["Total Reviews"].append(total_reviews)

            print(f"totalPages : {self.totalPages} " + f"currentPage : {self.currentPage} " + f"pagesToGo : {self.pagesToGo}")
            if self.currentPage <= self.totalPages and self.currentPage <= self.pagesToGo:

                if self.requestCount//3 == 0:
                    self.new_auth_token()

                randomTime = random.randint(50, 200)
                print(f"Sleeping for {randomTime} seconds")
                time.sleep(randomTime)
                self.currentPage += 1
                print(f"Next Page: {self.currentPage}")
                self.priority -= 10000
                self.requestCount += 1
                goToUrl = self.start_urls[0].format(self.currentPage, self.eachPage)
                yield scrapy.Request(
                    url=goToUrl,
                    callback=self.parse,
                    priority=self.priority,
                    headers=self.headers
                )

            # self.priority -= 1000
            # # sleepTime = random.randint(5,10)
            # # print(f"Sleeping for {sleepTime} seconds before fetching author data for {id}")
            # # time.sleep(sleepTime)
            # yield scrapy.Request(
            #     url=review_data_url,
            #     callback=self.parse_reviews,
            #     priority=self.priority,
            #     headers=self.headers,
            #     meta={"id": id}
            # )

    def new_auth_token(self):
        url = "https://www.crunchyroll.com/auth/v1/token"
        headers = {
            'authority': 'www.crunchyroll.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': 'Basic Y3Jfd2ViOg==',
            'content-type': 'application/x-www-form-urlencoded',
            'cookie': 'cf_clearance=iO9FZ9e0koQODNoUBQW1ZGOMfv71P4k37pcS2qEQ4yI-1710933704-1.0.1.1-cU7uwb.uIltSfsPC3kne8bjF52T9XdsS65XdnDFkeYx6Os0aAmYf2znC0dEBmuaCZafMwCN80hUen8BqMazXvQ; ajs_anonymous_id=43a804b7-de6e-4c0a-b63e-4171ae61ad9a; OptanonAlertBoxClosed=2024-03-20T11:27:08.115Z; __cf_bm=xX6Tk8GO0Apjzjz3r_pML0XdHUfrKwhzAZNuh0Df7Dg-1710935623-1.0.1.1-WHvkJmn.lESETAdpw1HTuAU1.VT4f3TlhM6kqLc8L7QJJZscS4Ufz4HP0FYBrGkxVDmr_Zz2NYsJoh1tsO8YRFbWeqUId7QjSYPjSyWJZgA; SSRT_GuUe=S876ZQADAA; OptanonConsent=isGpcEnabled=0&datestamp=Wed+Mar+20+2024+17%3A23%3A47+GMT%2B0530+(India+Standard+Time)&version=202402.1.0&browserGpcFlag=0&isIABGlobal=false&hosts=&consentId=0ece8ce1-23be-4a6c-becd-e9e0231330e8&interactionCount=1&isAnonUser=1&landingPath=NotLandingPage&groups=C0001%3A1%2CC0003%3A0%2CC0002%3A0%2CC0004%3A0&AwaitingReconsent=false&geolocation=IN%3BCG; _dd_s=rum=2&id=7eac55ab-0b0b-4544-9ff7-c24f1b45c131&created=1710933703565&expire=1710936891029',
            'origin': 'https://www.crunchyroll.com',
            'referer': 'https://www.crunchyroll.com/videos/alphabetical',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"macOS"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
        data = {'grant_type': 'client_id'}
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get('access_token')
            self.headers['authorization'] = f"Bearer {access_token}"
            print(f"New token: {access_token}")
            return access_token
        else:
            print(f"Failed to retrieve token. Status code: {response.status_code}")
            return None


    def get_review_count(self , url): #pass headers in it too
        if self.requestCount//3 == 0:
            self.new_auth_token()
        self.requestCount += 1
        response = requests.get(url , headers=self.headers)
        jsonResponse = json.loads(response.text)
        total = jsonResponse.get("total" , 0)
        return total
    
    # def get_published_data(self , url):
    #     if self.requestCount//3 == 0:
    #         self.new_auth_token()
    #     self.requestCount += 1
    #     response = requests.get(url , headers=self.headers)
    #     jsonResponse = json.loads(response.text)
    #     data = jsonResponse.get("data" , {})
    #     publisher = data[0].get("content_provider" , "")
    #     return publisher

        
    def parse_reviews(self, response):
        if not response.text:
            self.logger.warning(f"Skipping {response.url} as no data is being returned")
            return

        id = response.meta["id"]

        jsonResponse = json.loads(response.text)
        total = jsonResponse.get("total" , 0)

        self.output_dict["Total Reviews"].append(total)

        print(f"totalPages : {self.totalPages} " + f"currentPage : {self.currentPage} " + f"pagesToGo : {self.pagesToGo}")
        if self.currentPage <= self.totalPages and self.currentPage <= self.pagesToGo:
            randomTime = random.randint(50, 200)
            print(f"Sleeping for {randomTime} seconds")
            # time.sleep(randomTime)
            self.currentPage += 1
            print(f"Next Page: {self.currentPage}")
            self.priority -= 10000
            goToUrl = self.start_urls[0].format(self.currentPage, self.eachPage)
            yield scrapy.Request(
                url=goToUrl,
                callback=self.parse,
                priority=self.priority,
                headers=self.headers
            )


        

    def closed(self, reason):
        df = pd.DataFrame(self.output_dict)
        df.to_csv(f"out/{self.name}.csv", index=False)


def main():
    process = CrawlerProcess()

    start_urls = ["https://www.crunchyroll.com/content/v2/discover/browse?start={}&n={}&sort_by=popularity&categories=sci-fi&ratings=true&locale=en-US"]

    output_dict = {
        "Id" : [],
        "URL": [],
        "Title": [],
        "Rating": [],
        "Total Ratings": [],
        "% of 5-star+4-star Reviews": [],
        "Total Reviews" : [],
        "Episode Count": [],
        "Introduction": [],
        "Tags": [],
        "Publisher": [],
        "Audio for Education Purpose": []
    }

    process.crawl(
        CrunchyrollListing,
        start_urls=start_urls,
        output_dict=output_dict
    )
    process.start()


if __name__ == "__main__":
    main()