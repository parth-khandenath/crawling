import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc
import json
import os
from csv import DictWriter

class WebtoonSelenium:
    def __init__(self):
        self.file_name = 'kakao-webtoon.csv'
        self.books_done=0
        self.skip=True
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
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f"--origin=https://webtoon.kakao.com")
        chrome_options.add_argument(f"--referer=https://webtoon.kakao.com/")
        chrome_options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36")
        chrome_options.add_argument(f"--cookie=_kpdid=4169b78d46a94e22bfd1c25317dd98d0; _kpiid=4990a512cfa11e3046b3e794d5886deb; theme=dark; _gcl_au=1.1.1734905378.1708003378; _kp_collector=KP.3134594333.1708003378113; _ga=GA1.2.1180757148.1708003378; _gid=GA1.2.1664152839.1708003378; _gat_UA-200265735-2=1; _ga_GLWD7GS60Q=GS1.2.1708003378.1.0.1708003378.60.0.0; _fbp=fb.1.1708003378877.1072315077; _T_ANO=Qq+I/lWpcl6DH4KfTbqDupWMttiR4k/FGexpWR1EIYLRHKR3BuOlfmbME6+rp64c5wRcjn0/GmnWi/4K0zoGJ75aPXMIhDUElZbl8DZ/Qh+i85ZOXbgH/3Hl2OsSzsT9fyO5EM6OzvJE6xdOAslrEclRb12cbzkdFwgio7C+Lu4aL/VmgkfA3fhc2TEo7lqG5ocNBGPsUNgevBL7aSMsmJCd2HhlxxQmAeUiz2HXvmGPl094TPGi59pIxSd2eJgmTvorMoBEOsZDyjwMMn/ENTcKx+uhWd2IDo50dfeh6NmZHzHSlncMYLQ3RrDkDkNrJ6pS12mi8fLPR5WTZwh1RA==; _ga_80D69HE0QD=GS1.1.1708003378.1.1.1708003399.0.0.0")
        chrome_options.add_argument("--headless")  # Uncomment this line if you want to run headless
        driver = webdriver.Chrome(options=chrome_options)

        try:
            driver.get("https://gateway-kw.kakao.com/section/v1/timetables/days?placement=timetable_completed")
            time.sleep(2) 

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
        if book_url=='https://webtoon.kakao.com/content/그녀와-32분의-1/1070':
            self.skip=False
        if self.skip:
            return
        print('inside parse_book:', book_url)
        try:
            driver.get(book_url)
        except TimeoutError:
            time.sleep(10)
            driver.get(book_url)
        if self.books_done%40 ==0:
            time.sleep(23)
        time.sleep(2)  

        if meta['adult']:
            genre = "NA"
            views = "NA"
            likes = "NA"
        else:
            try:
                info = driver.find_elements(By.CSS_SELECTOR,'.ml-2')
                genre = info[0].text
                views = info[1].text
                likes = info[2].text
            except Exception as e:
                print(e)
                genre = "NA"
                views = "NA"
                likes = "NA"

        meta['views'] = views
        meta['genre'] = genre
        meta['likes'] = likes
        meta['p'] = meta['p'] - 10

        url = f'https://gateway-kw.kakao.com/decorator/v2/decorator/contents/{meta["book_id"]}/profile'
        self.get_more(driver, url, meta)

    def get_more(self, driver, url, meta):
        print('inside get_more:', url)
        driver.get(url)
        time.sleep(1.5)  # Add a sleep to ensure the page is loaded

        soup = BeautifulSoup(driver.page_source, "lxml")
        res_json = json.loads(soup.text)
        # print(meta['book_url'])
        # print(res_json)

        meta['title'] = res_json['data']['title']
        summary = res_json['data']['synopsis']

        rcmnds = []
        rclst = []

        if res_json['data']['recommendations']:
            rclst = res_json['data']['recommendations'][0]['contents']

        for r in rclst:
            rcmnds.append({
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
        self.books_done+=1
        self.append_list_as_row(self.file_name, data)


if __name__ == "__main__":
    webtoon_scraper = WebtoonSelenium()
    webtoon_scraper.scrape()
