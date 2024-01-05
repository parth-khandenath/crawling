import undetected_chromedriver as uc
from bs4 import BeautifulSoup 
import re
import time
import pandas as pd
import requests

def find_right_date(type,start_ind,chapter_times):
    m=1
    if type=="last":
        m=-1
    right_date=chapter_times[start_ind][-19:-9]
    next=1  #checking for a valid start date
    while not check(right_date) and next<=10 and start_ind+m*next<len(chapter_times) and start_ind+m*next>0:
        right_date=chapter_times[start_ind+m*next][-19:9]
        next+=1
    if not check(right_date):
        return "N/A"
    return right_date

def check(date):
    date_pattern = r'\b\d{4}-\d{2}-\d{2}\b'
    # valid_chars=['0','1','2','3','4','5','6','7','8','9','-']
    dates = re.findall(date_pattern, date)
    return len(dates)==1

df_header={
            'title': [],
            'book_id':[],
            'author': [],
            'tags': [],
            'approx_num_chapts': [],
            'status':[],
            'approx_novel_start':[],
            'last_chapter_time':[],
            'words': [],
            'url': [],
            'reads': [],
            'total_recomendations': [],
            'weekly_recomendations': []
        }

try:
    ans=pd.read_csv('4yt.csv')
except:
    ans=pd.DataFrame(df_header)

options = uc.ChromeOptions() 
options.page_load_strategy = 'eager'
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
driver = uc.Chrome(options=options)

last_page=621 #change here
page_no=1
while True:
    try:
        if page_no>last_page:
            print("breaking at page:",page_no)
            break
        print("trying page:",page_no)
        driver.get(f'https://www.4yt.net/all/book/0_0_0_0_0_4.html?keyword=&fuzzySearchType=1&page={page_no}')
        soup1=BeautifulSoup(driver.page_source,'lxml')
        book_urls_eles = soup1.select('.bookName a')
        book_urls=[]
        for ele in book_urls_eles:
            book_urls.append(ele.get_attribute('href'))
        # print("########")
        # print(book_urls)

        base_url = 'https://www.4yt.net'
        for book_link in book_urls:
            if not 'www' in book_link:
                if book_link[0]!='/':
                    book_link='/'+book_link
                book_link=base_url+book_link

            driver.get(book_link) #book  opened
            soup2=BeautifulSoup(driver.page_source,'lxml')
            title = soup2.select_one('div.book-head div.cont span.h1').text
            author = soup2.select_one('div.book-head div.cont span.h2').text
            status=soup2.select_one('a.blue').text
            if status=='完本小说':
                status='completed'
            elif status=='连载中':
                status='ongoing'

            chapter_times_eles= soup2.select('.volume dd a')
            chapter_times=[]
            for ele in chapter_times_eles:
                chapter_times.append(ele.get_attribute('title'))
            approx_num_chapts=len(chapter_times) 
            #finding approx novel start time
            # approx_novel_start=chapter_times[0][-19:-9]
            start=0
            if len(chapter_times)>12:  #recommendation section (to be skipped)
                # approx_novel_start=chapter_times[12][-19:-9] 
                start=12 #skipped 12 links (assuming recommendation)
            approx_novel_start=find_right_date("start",start,chapter_times)
            last_chapter_time=find_right_date("last",approx_num_chapts-1,chapter_times)

            tags_eles = soup2.select('div.book-head div.label a.green')
            tags=[]
            for ele in tags_eles:
                tags.append(ele.text)
            words = soup2.select_one('div.book-head div.count span.num[id="word_info"]').text
            # chapters_info = response.css('div.book-list dt span.info::text').getall()
            book_id=book_link.split('/')[-1][:-5]
            other_url = f'https://www.4yt.net/ck/book/{book_id}/databox?appKey=3156022953'

            # driver.get(other_url) #same book other page opened
            response=requests.get(other_url)
            res_json = response.json()
            reads = res_json['data']['pv']
            total_recomendations = res_json['data']['recommentTicket']
            weekly_recomendations = res_json['data']['week']['recommentTicket']

            ans.loc[len(ans.index)]=[title,book_id,author,tags,approx_num_chapts,status,approx_novel_start,last_chapter_time,words,book_link,reads,total_recomendations,weekly_recomendations]
            ans.to_csv('4yt.csv',index=False)

        print("page done:",page_no)
        page_no+=1
    except Exception as e:
        print("err:",e)
        pass