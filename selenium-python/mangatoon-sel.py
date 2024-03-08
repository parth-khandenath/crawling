import time
import os
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup
from csv import DictWriter

class MangatoonScraper:
    def __init__(self):
        self.file_name = 'mangatoon.csv'
        self.df_header = {
            "id": [], "title": [], "url": [], "views": [], "likes": [], "tags": [],
            "status": [], "rating": [], "authorName": [], "description": []
        }

    def initialize_driver(self):
        options = uc.ChromeOptions()
        # options.add_argument('--headless')  # Uncomment this line if you don't want the browser to be visible
        self.driver = uc.Chrome(options=options)
        # return driver

    def append_list_as_row(self, list_of_elem):
        file_exists = os.path.isfile(self.file_name)
        with open(self.file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def scrape(self):
        # driver = 
        self.initialize_driver()
        start_page=33   #change here  #actual start - page=0
        last_page=141
        try:
            for i in range(start_page, last_page + 1):
                print('page:',i)
                url = f'https://mangatoon.mobi/en/genre/comic?page={i}'
                self.driver.get(url)
                time.sleep(3)  # Add a delay to wait for the page to load (you may need to adjust this)

                soup = BeautifulSoup(self.driver.page_source, 'lxml')

                book_links = soup.select(".items a")
                likes = soup.select('.heart+ span')
                titles = soup.select('.content-title span')
                tags_lst = soup.select('.content-tags span')
                for i in range(len(book_links)):
                    link=book_links[i]
                    like=likes[i].text
                    title=titles[i].text
                    tags=tags_lst[i].text
                    book_link = link.get('href')
                    book_id = book_link.split('=')[-1]
                    book_link='https://mangatoon.mobi'+book_link
                    self.scrape_book(book_link, book_id, like, title, tags)
        finally:
            pass
            # driver.quit()

    def scrape_book(self, book_link, book_id, like, title, tags):
        self.driver.get(book_link)
        print(book_link)
        time.sleep(3)  # Add a delay to wait for the page to load (you may need to adjust this)
        try:
            iframe = self.driver.find_element(By.CSS_SELECTOR,'iframe[title="reCAPTCHA"]')
        except NoSuchElementException:
            iframe=None
        if iframe:
            print('################')
            print('SOLVE CAPTCHA !!')
            print('################')
            time.sleep(120)
            # soup = BeautifulSoup(self.driver.page_source,'lxml')
        soup = BeautifulSoup(self.driver.page_source,'lxml')
        if like[-1] == 'M':
            like = int(float(like[:-1]) * 1000000)
        elif like[-1] == 'k':
            like = int(float(like[:-1]) * 1000)

        try:
            # title = soup.select_one('.detail-title').text
            status = soup.select_one('.detail-status').text
            views = soup.select_one('.view-count').text
            if views[-1] == 'M':
                views = int(float(views[:-1]) * 1000000)
            elif views[-1] == 'k':
                views = int(float(views[:-1]) * 1000)
            # like = soup.select_one('.like-count').text
            rating = soup.select_one('.detail-score-points').text
            author_name = soup.select_one('.detail-author-name span').text
            author_name=author_name.split(':')[1].strip()
            description = soup.select_one('.detail-description-all p').text
            # tags = [tag.text for tag in soup.select('.detail-info a')]
        except Exception as e:
            status='NA'
            views='NA'
            rating='NA'
            author_name='NA'
            description='NA'
            print(e)
            # return

        data = {
            'id': 'mangatoon-' + str(book_id),
            'title': title,
            'url': book_link,
            'views': views,
            'likes': like,
            'tags': tags,
            'status': status,
            'rating': rating,
            'authorName': author_name,
            'description': description
        }

        self.append_list_as_row(data)


if __name__ == "__main__":
    scraper = MangatoonScraper()
    scraper.scrape()
