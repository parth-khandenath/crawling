import scrapy
import re
import pandas as pd


class DreameSpider(scrapy.Spider):
    name = "dreame"
    allowed_domains = ["www.dreame.com"]
    start = 1
    end = 10
    data_url = "https://www.dreame.com/all-genres/8-ya-teenfiction.html?page={}"

    start_urls = [data_url.format(start)]
    priority = 100000000
    headers = {
        "Title": [],
        "Url": [],
        "BookId": [],
        "Author": [],
        "Genre": [],  # Werewolf
        "Tags": [],
        "Reads Count": [],
        "Follow Count": [],
        "Authorized": [],
        "Age": [],
        "Description": [],
    }
    ans = pd.DataFrame(headers)

    def convert_views(self, views_str):

        suffix_mapping = {"M": 1000000, "K": 1000}
        if views_str[
            -1
        ].isdigit():  # Check if the last character is a digit (no suffix present)
            return int(views_str)
        else:
            views = float(
                views_str[:-1]
            )  # Convert the numerical part to float, excluding the last character (suffix)
            suffix = views_str[-1]  # Get the last character (suffix)
            if suffix in suffix_mapping:
                return int(views * suffix_mapping[suffix])
            else:
                return None

    def parse(self, response):
        booklist = response.css(".column_book-name__wyITG a ::attr(href)").getall()
        for book in booklist:
            link = "https://www.dreame.com" + book
            print(link)
            yield response.follow(
                link,
                callback=self.bookdata,
                meta={"url": link},
                priority=self.priority - 100,
            )

        if self.start > self.end:
            return

        self.start += 1
        nextpage = self.data_url.format(self.start)
        yield response.follow(nextpage, callback=self.parse)

    def bookdata(self, response):
        print("**************")
        url = response.meta["url"]
        bookid = url.split("/")[-1].split("-")[0]
        title = response.css(".story_novel-name__kRaIp ::text").get().strip()
        genre = "ya-teenfiction"
        tags = "-".join(response.css(".story_novel-tag-item__RqkdL ::text").getall())
        author = response.css(".story_author-name__sInbS span ::text").get().strip()

        follow_count = response.css(".story_data-num__M4pvn ::text").getall()[0].strip()
        read_count = response.css(".story_data-num__M4pvn ::text").getall()[1].strip()
        follow_count = self.convert_views(follow_count)
        read_count = self.convert_views(read_count)

        try:
            isauthorised = response.css(" .story_novel-auth-tag__p3K6e span").geta()
            isauthorised = True
        except:
            isauthorised = False

        ageres = response.css(".story_novel-limit-tag__JCQUM span ::text").get().strip()
        intro = response.css(".intr_unfold__7VWId ::text").get().strip()
        intro = re.sub(r"\s+", " ", intro).strip()
        intro = intro.replace("\n", " ")

        self.ans.loc[len(self.ans.index)] = [
            title,
            url,
            bookid,
            author,
            genre,
            tags,
            read_count,
            follow_count,
            isauthorised,
            ageres,
            intro,
        ]

        self.ans.to_csv("dreame-ya-teenfiction.csv", index=False)