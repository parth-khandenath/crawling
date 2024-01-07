import undetected_chromedriver as uc
from bs4 import BeautifulSoup 
import re
import json
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
headers = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
  'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'Cache-Control': 'max-age=0',
  'Connection': 'keep-alive',
  'Cookie': 'acw_tc=276077b917046094756303804e4967f370b9ffd3f9d8c34ddd52e5a9541a18; acw_sc__v2=659a46c343c05b441a3f80b17bbd0e556273a2f8',
  'Referer': 'https://www.4yt.net/ck/book/332013/databox?appKey=3156022953',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"'
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
        book_urls_eles = soup1.find_all("a",class_='bookcover',href=True)
        book_urls=[]
        for ele in book_urls_eles:
            book_urls.append(ele['href'])#.get_attribute('href'))
        print("length:",len(book_urls))
        if len(book_urls)==0:
            raise Exception("books not loaded")
        base_url = 'https://www.4yt.net'
        for book_link in book_urls:
            if not 'www' in book_link:
                if book_link[0]!='/':
                    book_link='/'+book_link
                book_link=base_url+book_link

            driver.get(book_link) #book  opened
            soup2=BeautifulSoup(driver.page_source,'lxml')
            # title = soup2.select_one('div.book-head div.cont span.h1').text
            title = soup2.find('span',class_='h1').text
            print("a")
            # author = soup2.select_one('div.book-head div.cont span.h2').text
            author = soup2.find('span',class_='h2').text
            print("b")
            status=soup2.find('a',class_='blue').text
            print("c")
            if status=='完本小说':
                status='completed'
            elif status=='连载中':
                status='ongoing'

            chapter_times_eles= soup2.select('.volume dd a')
            # print(chapter_times_eles)
            chapter_times=[]
            for ele in chapter_times_eles:
                ele.ge
                chapter_times.append(ele['title'])
            approx_num_chapts=len(chapter_times) 
            print("d")
            #finding approx novel start time
            # approx_novel_start=chapter_times[0][-19:-9]
            start=0
            if len(chapter_times)>12:  #recommendation section (to be skipped)
                # approx_novel_start=chapter_times[12][-19:-9] 
                start=12 #skipped 12 links (assuming recommendation)
            approx_novel_start=find_right_date("start",start,chapter_times)
            print("e")
            last_chapter_time=find_right_date("last",approx_num_chapts-1,chapter_times)
            print("f")

            tags_eles = soup2.select('div.book-head div.label a.green')
            tags=[]
            for ele in tags_eles:
                tags.append(ele.text)
            tags='-'.join(tags)
            print("g")
            words = soup2.select_one('div.book-head div.count span.num[id="word_info"]').text
            print("h")
            # chapters_info = response.css('div.book-list dt span.info::text').getall()
            book_id=book_link.split('/')[-1][:-5]
            
            other_url = f'https://www.4yt.net/ck/book/{book_id}/databox?appKey=3156022953'
            attempts=0
            # driver.get(other_url) #same book other page opened
            while(True):
                try:
                    attempts+=1
                    response=requests.request("GET",other_url,headers=headers,timeout=60)
                    if len(response.text)==0 or response.status_code!=200:
                        raise Exception("api call empty response")
                    # print(response.text)
                    res_json =json.loads(response.text)
                    reads = res_json['data']['pv']
                    print("i")
                    total_recomendations = res_json['data']['recommentTicket']
                    print("j")
                    weekly_recomendations = res_json['data']['week']['recommentTicket']
                    print("k")
                    break
                except Exception as e:
                    print("attempt:",attempts)
                    print("eeeeer:",e)
                    if attempts<3:
                        print("retrying in 5 secs..")
                        time.sleep(5)
                    else:
                        reads="N/A"
                        total_recomendations="N/A"
                        weekly_recomendations="N/A"
                        break
            print('book done')

            ans.loc[len(ans.index)]=[title,book_id,author,tags,approx_num_chapts,status,approx_novel_start,last_chapter_time,words,book_link,reads,total_recomendations,weekly_recomendations]
            ans.to_csv('4yt.csv',index=False)

        print("page done:",page_no)
        page_no+=1
    except Exception as e:
        print("err:",e)
        pass