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
options = uc.ChromeOptions() 

options.add_argument("--authority=api.babelnovel.com")
options.add_argument("--cookie=_gcl_au=1.1.1914344749.1705391269; _fbp=fb.1.1705391270100.527150223; _gid=GA1.2.1973026431.1706096729; cf_clearance=SB3oR8CM3MBWP97.DYFGiz9Zc.jHFJI.uBH3BG3LMZQ-1706160274-1-AXfQOtnv2NFMsc740+rtp6Hh6O8bCtCucof0ETtnJgaqYymttQGDBhV4+oN0mcOA6V40M+9ObXuBPtC3V1e4d9Y=; _ga=GA1.2.1495954902.1705391269; _uetsid=13006440baae11ee95996bd51480a4e4; _uetvid=8feddb00b44311ee89e9fdb80d6593fd; ajs_anonymous_id=%2200311626-8b61-4d54-b1e2-f4ed4abdfcf4%22; __gads=ID=847ac9005391bf53:T=1705391291:RT=1706160295:S=ALNI_MaQDepY6rvWM2ZOEJqGmuXtVHIjPw; __gpi=UID=00000cdf2739b9f7:T=1705391291:RT=1706160295:S=ALNI_MZCx5nSivhcie68VPTiOGXYUz5egw; _ga_0Z0KQGSTHR=GS1.1.1706159884.3.1.1706161743.0.0.0")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
driver = uc.Chrome(options=options)

requests=0
for gender in ['male-lead', 'female-lead','original']:
    # if gender == 'male-lead':
    #     continue
    try:
        ans=pd.read_csv(f"babel-{gender}.csv")
    except:
        ans=pd.DataFrame(headers)
    page_number = 0
    if gender=='male-lead':
        continue
    if gender=='female-lead':
        page_number=105
    while True:
        if gender=='male-lead':
            if page_number==123: #change here
                print("male done...")
                break
        elif gender=='female-lead':
            if page_number==157: #change here
                print("female done...")
                break
        else: #original
            if page_number==137: #change here
                print('original done...')
                break
        if gender in ['male-lead', 'female-lead']:
            link = f"https://api.babelnovel.com/v1/books?orderBy=week&languageCode=en&topClass=webnovel&targetAudience={gender}&page={page_number}&pageSize=20&fields=id,name,canonicalName,genres,cover,subTitle,synopsis,translatorId,ratingNum,markedUp,releasedChapterCount,enSerial,readingTrend"
        elif gender=='original': #for western -- https://babelnovel.com/browse?groupType=western&orderBy=week&languageCode=en (original)
            link=f"https://api.babelnovel.com/v1/books?orderBy=week&languageCode=en&topClass={gender}&targetAudience=&page={page_number}&pageSize=20&fields=id,name,canonicalName,genres,cover,subTitle,synopsis,translatorId,ratingNum,markedUp,releasedChapterCount,enSerial,readingTrend"
        driver.get(link)
        requests+=1
        if requests%150==0:
            time.sleep(20)
        soup = bs(driver.page_source,"lxml")
        data = json.loads(soup.text)
        page_data = data["data"]
        if data["data"] == []:
            print('received empty data array.. breaking..')
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
                    requests+=1
                    if requests%150==0:
                        time.sleep(20)
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
        ans.to_csv(f"babel-{gender}.csv",index=False)
        print(f"gender:{gender} , page no done:{page_number}")
        page_number += 1
    ans = pd.DataFrame(headers) 
    time.sleep(15)