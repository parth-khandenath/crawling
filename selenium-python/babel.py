import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import json
import time
import pandas as pd
headers = {
    "Name":[],
    "bookId":[],
    "alternateTitle":[],
    "Views":[],
    "URL":[],
    "Rating":[],
    "No. of Ratings":[],
    "Genre":[],
    "Total Chapters":[],
    "createTime":[],
    "lastUpdateTime":[],
    "Status":[],    
    "Tags":[]
}
ans = pd.DataFrame(headers)

cu = 0
driver = uc.Chrome()
for gender in ['male', 'female']:
    if gender == 'male':
        continue
    try:
        ans=pd.read_csv(f"babel-{gender}-lead.csv")
    except:
        ans=pd.DataFrame(headers)
    page_number = 0
    if gender=='female':
        page_number=66
    while True:
        # female-lead
        if gender=='male':
            if page_number==123:
                print("male done...")
                break
        else:
            if page_number==157:
                print("female done...")
                break
        link = f"https://api.babelnovel.com/v1/books?orderBy=week&languageCode=en&topClass=webnovel&targetAudience={gender}-lead&page={page_number}&pageSize=20&fields=id,name,canonicalName,genres,cover,subTitle,synopsis,translatorId,ratingNum,markedUp,releasedChapterCount,enSerial,readingTrend"
        driver.get(link)
        soup = bs(driver.page_source,"lxml")
        data = json.loads(soup.text)
        page_data = data["data"]
        if data["data"] == []:
            break
        for entry in page_data:
            try:
                name = entry["name"]
                views = entry["readingTrend"]
                canonicalName = entry["canonicalName"]
                url =  "https://babelnovel.com/books/"+canonicalName
                # d1.get(url)
                # soup1 = bs(d1.page_source,"lxml")
                # no_of_ratings = soup1.select_one('.book-info_edit-wrapper__2xE4R').text
                genre = entry["genres"][0]["name"]
                #     No meaningful data came, all dates same (2018 - 2021)
                first_chapter_publish_time = entry["genres"][0]["createTime"].split('T')[0]
                latest_chapter_publish_time = entry["genres"][0]["updateTime"].split('T')[0]
                total_chapters = entry["releasedChapterCount"]
                # total_chapter = soup1.select_one('.latest-chapter_title__1Bg53').text
                if entry["enSerial"] == "completed":
                    status = "completed"
                else:
                    status = "OnGoing"
                try:
                    rating = entry["ratingNum"]
                    if rating =='':
                        rating = '0'
                    else:
                        rating = format(float(rating), ".2f")
                except:
                    rating = '0'
                book_api = f"https://api.babelnovel.com/v2/books/{canonicalName}"
                try:
                    driver.get(book_api)
                    soup = bs(driver.page_source,"lxml")
                    book_data = json.loads(soup.text)
                    tags_list = book_data['data']['tags']
                    rating_count = book_data['data']['ratingCount']
                    tags = '-'.join(tags_list)
                except:
                    tags = ''
                book_id=f'babel-{canonicalName}'
                ans.loc[len(ans.index)] = [name,book_id,canonicalName,views,url,rating,rating_count,genre,total_chapters,first_chapter_publish_time,latest_chapter_publish_time,status,tags]
            except Exception as e:
                pass
            cu += 1
            print(f"Done {cu}")
        ans.to_csv(f"babel-{gender}-lead.csv",index=False)
        print(f"gender:{gender} , page no done:{page_number}")
        page_number += 1
    ans = pd.DataFrame(headers) 
    time.sleep(15)