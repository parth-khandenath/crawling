import scrapy
import re
import pandas as pd
import datetime
import os
from csv import DictWriter

Headers = {"book name","book id","URL","Genre","Author Name","Chapter Number","Views","Rating","Number of ratings","Status","first chapter published","Tags"}
def append_list_as_row(file_name, list_of_elem):
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
        writer = DictWriter(csvfile, fieldnames=Headers)
        if not file_exists:
            writer.writeheader()
        writer.writerow(list_of_elem)


class WebnovelListing(scrapy.Spider):
    all_categories=["All Time","Translated","Power Ranking","Originals","Monthly","Weekly","Trending Ranking"]
    name = 'Webnovel_new_Listing_v2'
    links = {
            "Webnovel Male All Time Translated Power Ranking": "&rankId=power_rank&listType=0&type=1&rankName=Power&timeType=1&sourceType=1&sex=1&signStatus=0",
            "Webnovel Male All Time Translated Trending Ranking": "&rankId=best_sellers&listType=0&type=1&rankName=Trending&timeType=1&sourceType=1&sex=1",
            "Webnovel Male All Time Originals Power Ranking": "&rankId=power_rank&listType=0&type=1&rankName=Power&timeType=1&sourceType=2&sex=1&signStatus=1",
            "Webnovel Male All Time Originals Trending Ranking": "&rankId=best_sellers&listType=0&type=1&rankName=Trending&timeType=1&sourceType=2&sex=1",
            "Webnovel Male Annual Translated Power Ranking": "&rankId=power_rank&listType=2&type=1&rankName=Power&timeType=1&sourceType=1&sex=1&signStatus=0",
            "Webnovel Male Annual Translated Trending Ranking": "&rankId=best_sellers&listType=2&type=1&rankName=Trending&timeType=1&sourceType=1&sex=1",
            "Webnovel Male Annual Originals Power Ranking": "&rankId=power_rank&listType=2&type=1&rankName=Power&timeType=1&sourceType=2&sex=1&signStatus=0",
            "Webnovel Male Annual Originals Trending Ranking": "&rankId=best_sellers&listType=2&type=1&rankName=Trending&timeType=1&sourceType=2&sex=1",
            "Webnovel Male Bi-annual Translated Power Ranking": "&rankId=power_rank&listType=3&type=1&rankName=Power&timeType=1&sourceType=1&sex=1&signStatus=0",
            "Webnovel Male Bi-annual Translated Trending Ranking": "&rankId=best_sellers&listType=3&type=1&rankName=Trending&timeType=1&sourceType=1&sex=1",
            "Webnovel Male Bi-annual Originals Power Ranking": "&rankId=power_rank&listType=3&type=1&rankName=Power&timeType=1&sourceType=2&sex=1&signStatus=0",
            "Webnovel Male Bi-annual Originals Trending Ranking": "&rankId=best_sellers&listType=3&type=1&rankName=Trending&timeType=1&sourceType=2&sex=1",
            "Webnovel Male Season Translated Power Ranking": "&rankId=power_rank&listType=4&type=1&rankName=Power&timeType=1&sourceType=1&sex=1&signStatus=0",
            "Webnovel Male Season Translated Trending Ranking": "&rankId=best_sellers&listType=4&type=1&rankName=Trending&timeType=1&sourceType=1&sex=1",
            "Webnovel Male Season Originals Power Ranking": "&rankId=power_rank&listType=4&type=1&rankName=Power&timeType=1&sourceType=2&sex=1&signStatus=0",
            "Webnovel Male Season Originals Trending Ranking": "&rankId=best_sellers&listType=4&type=1&rankName=Trending&timeType=1&sourceType=2&sex=1",
            "Webnovel Female All Time Translated Power Ranking": "&rankId=power_rank&listType=0&type=1&rankName=Power&timeType=1&sourceType=1&sex=2&signStatus=0",
            "Webnovel Female All Time Translated Trending Ranking": "&rankId=best_sellers&listType=0&type=1&rankName=Trending&timeType=1&sourceType=1&sex=2",
            "Webnovel Female All Time Originals Power Ranking": "&rankId=power_rank&listType=0&type=1&rankName=Power&timeType=1&sourceType=2&sex=2&signStatus=0",
            "Webnovel Female All Time Originals Trending Ranking": "&rankId=best_sellers&listType=0&type=1&rankName=Trending&timeType=1&sourceType=2&sex=2",
            "Webnovel Female Annual Translated Power Ranking": "&rankId=power_rank&listType=2&type=1&rankName=Power&timeType=1&sourceType=1&sex=2&signStatus=0",
            "Webnovel Female Annual Translated Trending Ranking": "&rankId=best_sellers&listType=2&type=1&rankName=Trending&timeType=1&sourceType=1&sex=2",
            "Webnovel Female Annual Originals Power Ranking": "&rankId=power_rank&listType=2&type=1&rankName=Power&timeType=1&sourceType=2&sex=2&signStatus=0",
            "Webnovel Female Annual Originals Trending Ranking": "&rankId=best_sellers&listType=2&type=1&rankName=Trending&timeType=1&sourceType=2&sex=2",
            "Webnovel Female Bi-annual Translated Power Ranking": "&rankId=power_rank&listType=3&type=1&rankName=Power&timeType=1&sourceType=1&sex=2&signStatus=0",
            "Webnovel Female Bi-annual Translated Trending Ranking": "&rankId=best_sellers&listType=3&type=1&rankName=Trending&timeType=1&sourceType=1&sex=2",
            "Webnovel Female Bi-annual Originals Power Ranking": "&rankId=power_rank&listType=3&type=1&rankName=Power&timeType=1&sourceType=2&sex=2&signStatus=0",
            "Webnovel Female Bi-annual Originals Trending Ranking": "&rankId=best_sellers&listType=3&type=1&rankName=Trending&timeType=1&sourceType=2&sex=2",
            "Webnovel Female Season Translated Power Ranking": "&rankId=power_rank&listType=4&type=1&rankName=Power&timeType=1&sourceType=1&sex=2&signStatus=0",
            "Webnovel Female Season Translated Trending Ranking": "&rankId=best_sellers&listType=4&type=1&rankName=Trending&timeType=1&sourceType=1&sex=2",
            "Webnovel Female Season Originals Power Ranking": "&rankId=power_rank&listType=4&type=1&rankName=Power&timeType=1&sourceType=2&sex=2&signStatus=0",
            "Webnovel Female Season Originals Trending Ranking": "&rankId=best_sellers&listType=4&type=1&rankName=Trending&timeType=1&sourceType=2&sex=2"
            }
    file_name = ''
    start_urls = ['https://www.webnovel.com/stories/novel']
    custom_settings = {
        'DUPEFILTER_CLASS': 'scrapy.dupefilters.BaseDupeFilter',
        'CONCURRENT_REQUESTS': 1
    }
    
    def parse(self, response):
        cookie = response.headers.getlist(b'Set-Cookie')[0]
        print("Cookie is :", cookie)
        cookie = str(cookie)
        csrf = cookie.split(';')[0].split('=')[-1]
        for catalogue_name, catalogue_url in self.links.items():
            self.file_name = catalogue_name
            # print("********",catalogue_name)
            for i in range(1, 11):
                p = i * 1000
                url = f"https://www.webnovel.com/go/pcm/category/getRankList?_csrfToken={csrf}&pageIndex={str(i)}" + catalogue_url
                yield response.follow(url=url, priority=-p, meta={'csrf': csrf, 'p': -p,'catalogue_name':catalogue_name}, callback=self.parse_page)


    def parse_page(self, response):
        csrf = response.meta['csrf']
        p = int(response.meta['p'])
        p-=100
        book_items = response.json()['data']['bookItems']
        for i in range(len(book_items)):
            book_id = book_items[i]['bookId']
            book_name = book_items[i]['bookName']
            author = book_items[i]['authorName']
            categoryName = book_items[i]['categoryName']
            description = book_items[i]['description']
            firstChapter_publish_date = datetime.datetime.fromtimestamp(int(book_items[i]['publishTime']/1000))
            firstChapter_publish_date = firstChapter_publish_date.strftime('%Y-%m-%d')
            tags = book_items[i]['tagInfo']
            tags = [tag['tagName'] for tag in tags]
            tags = ','.join(tags)
            url = f'https://www.webnovel.com/go/pcm/bookReview/get-reviews?_csrfToken={csrf}&bookId={book_id}&pageIndex=1&pageSize=30&orderBy=1&novelType=0&needSummary=1&_=1682080583003'
            meta = {
                'book_id': book_id,
                'book_name': book_name,
                'author': author,
                'categoryName': categoryName,
                'description': description,
                'tags': tags,
                'firstChapter_publish_date':firstChapter_publish_date,
                'book_url':f'https://www.webnovel.com/book/{book_id}',
                'catalogue_name':response.meta['catalogue_name'],
                'p':p - 100* i
            }
            yield response.follow(url=url, priority=p - 100* i, meta=meta, callback=self.parse_book)

    def parse_book(self, response):
        baseInfo = response.json()['data']['baseInfo']
        views = baseInfo['pvNum']
        stats = response.json()['data']['bookStatisticsInfo']
        rating = stats['totalScore']
        totalReviewNum = stats['totalReviewNum']

        data = response.meta
        p = int(data['p'])
        data['rating'] = rating
        data['totalReviewNum'] = totalReviewNum
        data['views'] = views
        yield response.follow(url=data['book_url'],priority=p - 5, meta=data, callback=self.extract_chapters)


    def extract_chapters(self, response):
        meta = response.meta
 
        r = response.text
        completed = 'Not available'
        if '<span>Completed</span>' in r:
            completed = 'Completed'
        s = re.findall(r'chapterNum.*?,', r)
        lst = s
        text = lst[0]
        chapter_num = int(text.split(":")[1].strip(",}"))
        meta['chapterNum'] = chapter_num #chapter num
        book_data = dict.fromkeys(Headers)

        book_data["book name"] = meta['book_name']
        book_data["book id"] = meta['book_id']
        book_data["URL"] = meta['book_url']
        book_data["Genre"] = meta['categoryName']
        book_data["Author Name"] = meta['author']
        book_data["Chapter Number"] = chapter_num
        book_data["Views"] = meta['views']
        book_data["Rating"] = meta['rating']
        book_data["Number of ratings"] = meta['totalReviewNum']
        book_data["Status"] = completed
        book_data["first chapter published"] = meta['firstChapter_publish_date']
        book_data["Tags"] = meta['tags']

        append_list_as_row(meta['catalogue_name']+'.csv',book_data)