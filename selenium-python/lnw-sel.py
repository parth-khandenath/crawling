from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from csv import DictWriter
import os
import time

class LightnovelworldScraper:
    def __init__(self):
        chrome_options = uc.ChromeOptions()
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
        self.driver = uc.Chrome(options=chrome_options)
        self.file_name = "light-novel-world.csv"
        self.df_header = {'id': [], 'title': [], 'url': [], 'author': [], 'rank': [], 'rating': [], 'views': [],
                          'chapter_count': [], 'bookmarked': [], 'categories': [], 'summary': [], 'tags': []}

    def append_list_as_row(self, list_of_elem):
        file_exists = os.path.isfile(self.file_name)
        with open(self.file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
            writer = DictWriter(csvfile, fieldnames=self.df_header)
            if not file_exists:
                writer.writeheader()
            writer.writerow(list_of_elem)

    def scrape(self):
        for pg in range(1, 2):
            url = f'https://www.lightnovelworld.co/browse/genre-all-25060123/order-popular/status-all?page={pg}'
            self.scrape_page(url)
            

    def scrape_page(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR, "iframe[title='Widget containing a Cloudflare security challenge']")))

        # Find the element using JavaScript and click it
        element = WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label")))
        time.sleep(5)
        self.driver.execute_script("arguments[0].click();", element)

        # Wait for some time
        print('waiting..')
        # time.sleep(100)
        # self.driver.implicitly_wait(60)
        # time.sleep(5)
        # WebDriverWait(self.driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.CSS_SELECTOR,"iframe[title='Widget containing a Cloudflare security challenge']")))
        # WebDriverWait(self.driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "label.ctp-checkbox-label"))).click()
        # # return
        # print('waiting..')
        time.sleep(60)
        book_links = self.driver.find_elements(By.CSS_SELECTOR, 'h1.novel-title a')

        for bl in book_links:
            link = bl.get_attribute('href')
            id = link.split('-')[-1]
            if link[:6] == '/novel':
                self.parse_book('https://www.lightnovelworld.co' + link, id)
            else:
                self.parse_book(link, id)

    def parse_book(self, url, book_id):
        self.driver.get(url)
        title = self.driver.find_element(By.CSS_SELECTOR, '.novel-title').text
        author = self.driver.find_element(By.CSS_SELECTOR, 'div.author a.property-item span').text
        stats = self.driver.find_elements(By.CSS_SELECTOR, 'strong')
        rank, rating, chapter_count, views, bookmarked, status = [stat.text for stat in stats]

        category_eles = self.driver.find_elements(By.CSS_SELECTOR, 'li .property-item')
        categories = [ele.text for ele in category_eles]

        summary = ''
        p_eles = self.driver.find_elements(By.CSS_SELECTOR, '.summary p')
        for ele in p_eles:
            summary += ele.text

        tags = []
        tag_eles = self.driver.find_elements(By.CSS_SELECTOR, 'ul.content li')
        for ele in tag_eles:
            tags.append(ele.text)

        data = {
            'id': 'lightnovelworld-' + book_id,
            'title': title,
            'url': url,
            'author': author,
            'rank': rank,
            'rating': rating,
            'views': views,
            'chapter_count': chapter_count,
            'bookmarked': bookmarked,
            'categories': categories,
            'summary': summary,
            'tags': tags
        }
        self.append_list_as_row(data)

if __name__ == "__main__":
    scraper = LightnovelworldScraper()
    scraper.scrape()
