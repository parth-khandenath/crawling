from datetime import datetime
import time
import pandas as pd
import re
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import undetected_chromedriver as uc
# from selenium import webdriver

class AudibleScraper:
    def __init__(self):
        self.headers = {
            "Title": [],
            "Url": [],
            "Author": [],
            "Series": [],
            "Series Link": [],
            "Overall Rating": [],
            "Performance Rating": [],
            "Story Rating": [],
            "No. of  Ratings": [],
            "Total Length": [],
            "Release Date": [],
            "language": [],
            "Summary": [],
            "Tags": [],
            "Price": [],
            "page": [],
        }
        self.outputfilename = "audible-scifi-fantasy-695.csv"     #change here
        self.start_page=1   #change here
        self.last_page = 2   #change here
        self.base_url = "https://www.audible.com"
        try:
            self.ans=pd.read_csv(self.outputfilename)
        except:
            self.ans = pd.DataFrame(self.headers)

    def convert_date(self, date_string):
        parts = date_string.split("-")
        new_date_string = f"20{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        return new_date_string

    def scrape(self):
        # options = Options()
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }
        options = uc.ChromeOptions()
        options.page_load_strategy = 'eager'
        # options.add_argument('--headless')
        options.add_argument(f"--header={headers}")
        # service = Service('/path/to/chromedriver')
        # service.start()
        driver = uc.Chrome(options=options)

        sortorder= ["review-rank", "title-asc-rank"]

        for page_num in range(self.start_page, self.last_page + 1):
            # for order in sortorder:
            print("PAGE: ",page_num)
            url=f"https://www.audible.com/most-popular-listened-audiobooks?pageSize=50&searchCategory=18580606011&page={page_num}&ref_pageloadid=6JoYbLhh3SjoZpWe&ref=a_most-popu_c3_pageNum_0&pf_rd_p=0a7f3174-e7cd-49a5-9066-a739a18b0561&pf_rd_r=WE5HVB0H1897GWQMPY1Y&pageLoadId=mfQeLGlLVcfjraKo&creativeId=3680f922-7ac7-44de-b69b-045788aef7c1"
            # url = f"https://www.audible.com/search?feature_twelve_browse-bin=18685552011&ipRedirectOverride=true&node=18580606011&overrideBaseCountry=true&overrideBaseCountry=true&pageSize=50&sort=review-rank&page={page_num}&ref_pageloadid=T565g5fVDkfAXDiP&ref=a_search_c4_pageNum_4&pf_rd_p=1d79b443-2f1d-43a3-b1dc-31a2cd242566&pf_rd_r=5B22J28PWFG9QA126851&pageLoadId=glTRbdUrat8rggPz&creativeId=18cc2d83-2aa9-46ca-8a02-1d1cc7052e2a"
            driver.get(url)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, 'lxml')

            book_list = soup.select(".bc-heading a")
            n_ratings = soup.select(".ratingsLabel .bc-size-small")
            l_data = soup.select(".runtimeLabel .bc-size-small")
            r_data = soup.select(".releaseDateLabel .bc-size-small")
            p_data = soup.select(".buybox-regular-price span:nth-child(2)")
            la_data = soup.select(".languageLabel .bc-size-small")

            if page_num==86:
                book_list = book_list[-2:]

            print("books: ",len(book_list))

            for index, book in enumerate(book_list):
                link = self.base_url + book['href']
                link = link.split('?')[0]
                no_of_ratings = n_ratings[index].get_text(strip=True)
                length_data = l_data[index].get_text(strip=True)
                release_data = r_data[index].get_text(strip=True).split(":")[1].strip()
                release_data = release_data[:-2]+"20"+release_data[-2:]
                try:
                    price_data = p_data[index].get_text(strip=True)
                except:
                    price_data="NA"
                language_data = la_data[index].get_text(strip=True)

                driver.get(link)
                print("book link: ",link)
                time.sleep(6)
                book_soup = BeautifulSoup(driver.page_source, 'lxml')
                try:
                    goToAudiblecom = driver.find_element(By.CSS_SELECTOR,".customer-notification-banner a.bc-color-link")
                    goToAudiblecom.click()
                    time.sleep(4)
                    book_soup = BeautifulSoup(driver.page_source, 'lxml')
                except Exception as e:
                    print("error in finding banner ")
                    # print(e)
                
                title = book_soup.select_one("h1").get_text(strip=True)
                author = book_soup.select_one(".authorLabel a").get_text(strip=True)
                series = book_soup.select_one(".seriesLabel a")
                series = series.get_text(strip=True) if series else None
                series_link = self.base_url + book_soup.select_one(".seriesLabel a")['href'] if series else None

                try:
                    rating_data = book_soup.select_one(".bc-row-responsive > div:nth-child(1) .rating-stars .bc-color-secondary").get_text(strip=True)
                    rating = re.search(r"\d+\.\d+", rating_data).group()
                except:
                    rating = "NA"
                a = book_soup.select(".bc-row-responsive .rating-stars .bc-color-secondary")
                if rating == "NA":
                    try:
                        rating = a[0].get_text(strip=True)
                    except:
                        rating = "NA"
                p1 = r"\d+\.\d+"
                p2 = r"\d+\.\d+"
                try:
                    p_rating = a[1].get_text(strip=True)
                    performance_rating = re.search(p1, p_rating).group()
                except:
                    performance_rating = "NA"
                try:
                    s_rating = a[2].get_text(strip=True)
                    story_rating = re.search(p2, s_rating).group()
                except:
                    story_rating = "NA"

                no_of_ratings = no_of_ratings.split(" ")[0]

                numbers = re.findall(r"\d+", length_data)
                hours = int(numbers[0])
                try:
                    minutes = int(numbers[1])
                except:
                    minutes = 0
                total_length = hours * 60 + minutes

                release_date = self.convert_date(release_data)

                language = language_data.replace("Language:", "").strip()

                summary_data = book_soup.select("span.bc-text p")
                summary = " ".join([item.get_text(strip=True) for item in summary_data])

                tags_data = book_soup.select(".bc-chip-text")
                tags = "-".join([item.get_text(strip=True) for item in tags_data])

                price = price_data[1:]
                print()
                self.ans.loc[len(self.ans.index)] = [
                    title,
                    link,
                    author,
                    series,
                    series_link,
                    rating,
                    performance_rating,
                    story_rating,
                    no_of_ratings,
                    total_length,
                    release_date,
                    language,
                    summary,
                    tags,
                    price,
                    page_num
                ]
                self.ans.to_csv(self.outputfilename, index=False)

        driver.quit()
        # service.stop()

if __name__ == "__main__":
    audible_scraper = AudibleScraper()
    audible_scraper.scrape()
