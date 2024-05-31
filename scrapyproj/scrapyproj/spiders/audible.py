from datetime import datetime
import scrapy
import re
import pandas as pd


class AudibleSpider(scrapy.Spider):
    name = "audible"
    allowed_domains = ["www.audible.com"]
    # start_urls = [
    #     "https://www.audible.com/search?feature_twelve_browse-bin=18685552011&ipRedirectOverride=true&node=18580606011&overrideBaseCountry=true&overrideBaseCountry=true&pageSize=50&sort=review-rank&page=11&ref_pageloadid=T565g5fVDkfAXDiP&ref=a_search_c4_pageNum_4&pf_rd_p=1d79b443-2f1d-43a3-b1dc-31a2cd242566&pf_rd_r=5B22J28PWFG9QA126851&pageLoadId=glTRbdUrat8rggPz&creativeId=18cc2d83-2aa9-46ca-8a02-1d1cc7052e2a"
    # ]
    start_urls=[]
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 1,
        "User-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        }

    # start = 1
    # end = 25
    priority = 100000000  #5000  ->  2,00,000
    headers = {
        "Title": [],
        "Url": [],
        "Author": [],
        "Series": [],
        "Series Link": [],
        "Rating": [],
        "Performance Rating": [],
        "Story Rating": [],
        "No. of  Ratings": [],
        "Total Length": [],
        "Release Date": [],
        "language": [],
        "Summary": [],
        "Tags": [],
        "Price": [],
    }
    ans = pd.DataFrame(headers)

    def __init__(self):
        lastpage=40  #change here
        for pn in range(1,lastpage+1):
            self.start_urls.append(f"https://www.audible.com/search?feature_twelve_browse-bin=18685552011&ipRedirectOverride=true&node=18580606011&overrideBaseCountry=true&overrideBaseCountry=true&pageSize=50&sort=review-rank&page={pn}&ref_pageloadid=T565g5fVDkfAXDiP&ref=a_search_c4_pageNum_4&pf_rd_p=1d79b443-2f1d-43a3-b1dc-31a2cd242566&pf_rd_r=5B22J28PWFG9QA126851&pageLoadId=glTRbdUrat8rggPz&creativeId=18cc2d83-2aa9-46ca-8a02-1d1cc7052e2a")

    def convert_date(self, date_string):
        parts = date_string.split("-")
        new_date_string = f"20{parts[2]}-{parts[0].zfill(2)}-{parts[1].zfill(2)}"
        return new_date_string

    def parse(self, response):
        print("**************")
        print("GNL")
        booklist = response.css(".bc-heading a::attr(href)").getall()
        print("books:",len(booklist))
        n_ratings = response.css(".ratingsLabel .bc-size-small::text").getall()
        l_data = response.css(".runtimeLabel .bc-size-small::text").getall()
        r_data = response.css(".releaseDateLabel .bc-size-small::text").getall()
        p_data = response.css(".buybox-regular-price span:nth-child(2)::text").getall()
        la_data = response.css(".languageLabel .bc-size-small::text").getall()

        for index, book in enumerate(booklist):

            link = "https://www.audible.com" + book
            # print(link)
            no_of_ratings = n_ratings[index]
            length_data = l_data[index]
            release_data = r_data[index]
            price_data = p_data[index]
            language_data = la_data[index]

            self.priority -= 100
            yield response.follow(
                link,
                callback=self.bookdata,
                meta={
                    "url": link,
                    "no_of_ratings": no_of_ratings,
                    "length_data": length_data,
                    "release_data": release_data,
                    "price_data": price_data,
                    "language_data": language_data,
                },
                priority=self.priority,
            )
        # self.start += 1
        # print(self.start)
        # if self.start > 25:
        #     return
        # nextpage = (
        #     "https://www.audible.com" + response.css(".nextButton a::attr(href)").get()
        # )

        # yield response.follow(nextpage, callback=self.parse)

    def bookdata(self, response):
        title = response.css(" h1::text").get()
        url = response.meta["url"]
        author = response.css(".authorLabel a::text").get()
        if response.css(".seriesLabel a::text").get():
            series = response.css(".seriesLabel a::text").get()
        else:
            series = None
        if response.css(".seriesLabel a::attr(href)").get():
            series_link = (
                "https://www.audible.com"
                + response.css(".seriesLabel a::attr(href)").get()
            )
        else:
            series_link = None
        try:
            rating_data = response.css(
                ".bc-row-responsive > div:nth-child(1) .rating-stars .bc-color-secondary"
            ).get()
            pattern = r"\d+\.\d+"
            rating = re.search(pattern, rating_data).group()   #
        except:
            rating="NA"
        a = response.css(
            ".bc-row-responsive .rating-stars .bc-color-secondary::text"
        ).getall()
        if rating=="NA":
            try:
                rating=a[0]
            except:
                rating="NA"
        p1 = r"\d+\.\d+"
        p2 = r"\d+\.\d+"
        try:
            p_rating = a[1]
            performance_rating = re.search(p1, p_rating).group()
        except:
            performance_rating="NA"
        try:
            s_rating = a[2]
            story_rating = re.search(p2, s_rating).group()
        except:
            story_rating="NA"

        no_of_ratings = response.meta["no_of_ratings"]
        no_of_ratings = no_of_ratings.split(" ")[0]

        length_data = response.meta["length_data"]
        numbers = re.findall(r"\d+", length_data)
        hours = int(numbers[0])
        try:
            minutes = int(numbers[1])       #
        except:
            minutes=0
        total_length = hours * 60 + minutes

        # Convert to YYYY-MM-DD
        release_date = response.meta["release_data"]
        date_without_space = re.sub(r":\s+", ":", release_date)
        release_date = date_without_space.replace("Release date:", "").strip()
        release_date = self.convert_date(str(release_date))

        language_data = response.meta["language_data"].strip()
        language_without_space = re.sub(r":\s+", ":", language_data)
        language = language_without_space.replace("Language:", "").strip()

        summary_data = response.css("span.bc-text p::text").getall()
        summary = " ".join(summary_data)
        summary = re.sub(r"\s+", " ", summary).strip()

        tags_data = response.css(".bc-chip-text::text").getall()
        tags_dat = "-".join(tags_data)
        tags = re.sub(r"\s+", " ", tags_dat).strip()

        price_data = response.meta["price_data"].strip()
        price = price_data[1:]

        self.ans.loc[len(self.ans.index)] = [
            title,
            url,
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
        ]
        self.ans.to_csv("audible-scifi-fantasy.csv", index=False)   #change here

    #       def dateObjectFromDateString (self,date_string,date_format = "yyyy-mm-dd"):
    #     try:
    #         if date_format=="yyyy-mm-dd":
    #             date_object = datetime.strptime(date_string, "%Y-%m-%d").date()
    #         elif date_format=="dd/mm/yyyy":
    #             date_object = datetime.strptime(date_string, "%d/%m/%Y").date()
    #         date_time_object = datetime.combine(date_object, datetime.min.time())
    #         return date_time_object
    #     except Exception as e:
    #         print(e)
    #         return "NA"

    # def timestampFromDateString (self,date_string,date_format = "yyyy-mm-dd"):
    #     if date_format=="yyyy-mm-dd":
    #         date_object = datetime.strptime(date_string, "%Y-%m-%d").date()
    #     elif date_format=="dd/mm/yyyy":
    #         date_object = datetime.strptime(date_string, "%d/%m/%Y").date()
    #         unix_time = datetime.combine(date_object, datetime.min.time()).timestamp()
    #         timeStamp = int(unix_time)

    # p_rating = response.css(
    #     ".bc-row-responsive > div:nth-child(2) .rating-stars .bc-color-secondary::text"
    # ).get()
    # performance_rating = re.search(pattern, p_rating).group()

    # s_rating = response.css(
    #     ".bc-row-responsive > div:nth-child(3) .rating-stars .bc-color-secondary::text"
    # ).get()
    # story_rating = re.search(pattern, p_rating).group()