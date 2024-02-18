import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
import json
import os
from csv import DictWriter

class WebtoonSelenium:
    def __init__(self):
        self.file_name = 'kakao-webtoon.csv'
        self.df_header = {
            "title": [], "id": [], "adult": [], "url": [], "views": [], "genre": [], "likes": [], "author": [],
            "publisher": [], "summary": [], "keywords/tags": [], "related novels": []
        }

    def append_list_as_row(self, file_name, list_of_elem):
        file_exists = os.path.isfile(file_name)
        with open(file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def scrape(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Uncomment this line if you want to run headless
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get("https://gateway-kw.kakao.com/section/v1/timetables/days?placement=timetable_completed")
            time.sleep(2)  # Add a sleep to ensure the page is loaded

            soup = BeautifulSoup(driver.page_source, "lxml")
            res_json = json.loads(soup.text)

            p = 1000000
            count = 0

            for obj in res_json['data'][0]['cardGroups'][0]['cards']:
                count += 1
                title = obj['content']['seoId']
                book_id = str(obj['content']['id'])
                adult = obj['content']['adult']
                book_url = f'https://webtoon.kakao.com/content/{title}/{book_id}'
                author = []
                publisher = []

                for objj in obj['content']['authors']:
                    if objj['type'] == "AUTHOR":
                        author.append(objj['name'])
                    elif objj['type'] == 'PUBLISHER':
                        publisher.append(objj['name'])

                tags = obj['content']['seoKeywords']

                meta = {
                    'title': title,
                    'book_id': book_id,
                    'adult': adult,
                    'book_url': book_url,
                    'author': author,
                    'publisher': publisher,
                    'tags': tags,
                    'p': p - count * 100
                }

                self.parse_book(driver, book_url, meta)

        finally:
            driver.quit()

    def parse_book(self, driver, book_url, meta):
        driver.get(book_url)
        # time.sleep(2)  # Add a sleep to ensure the page is loaded

        if meta['adult']:
            genre = "NA"
            views = "NA"
            likes = "NA"
        else:
            info = driver.find_elements(By.CSS_SELECTOR,'.ml-2')
            genre = info[0].text
            views = info[1].text
            likes = info[2].text

        meta['views'] = views
        meta['genre'] = genre
        meta['likes'] = likes
        meta['p'] = meta['p'] - 10

        url = f'https://gateway-kw.kakao.com/decorator/v2/decorator/contents/{meta["book_id"]}/profile'
        self.get_more(driver, url, meta)

    def get_more(self, driver, url, meta):
        driver.get(url)
        time.sleep(1)  # Add a sleep to ensure the page is loaded

        soup = BeautifulSoup(driver.page_source, "lxml")
        print(soup)
        res_json = json.loads(soup.text)

        meta['title'] = res_json['data']['title']
        summary = res_json['data']['synopsis']

        rcmnds = []
        rclst = []

        if res_json['data']['recommendations']:
            rclst = res_json['data']['recommendations'][0]['contents']

        for r in rclst:
            rcmnds.append({
                'id': r['id'],
                'title': r['title'],
                'url': f"https://webtoon.kakao.com/content/{r['seoId']}/{r['id']}"
            })

        data = {
            'title': meta['title'],
            'id': 'kakaowebtoon-' + meta['book_id'],
            'adult': meta['adult'],
            'url': meta['book_url'],
            'views': meta['views'],
            'genre': meta['genre'],
            'likes': meta['likes'],
            'author': meta['author'],
            'publisher': meta['publisher'],
            'summary': summary,
            'keywords/tags': meta['tags'],
            'related novels': rcmnds
        }

        self.append_list_as_row(self.file_name, data)


if __name__ == "__main__":
    webtoon_scraper = WebtoonSelenium()
    webtoon_scraper.scrape()
