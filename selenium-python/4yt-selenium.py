import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
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
  'Accept-Language': 'en-US,en;q=0.9',
  'Connection': 'keep-alive',
  'Sec-Fetch-Dest': 'document',
  'Sec-Fetch-Mode': 'navigate',
  'Sec-Fetch-Site': 'none',
  'Sec-Fetch-User': '?1',
  'Upgrade-Insecure-Requests': '1',
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'Cookie': 'acw_tc=2760829817046480945665622e404ebd451f158ba251838414a9dcb42f143f'
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

last_page=622 #change here
page_no=1
# page_no=360
request_no=0
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
            # time.sleep(2)
            soup2=BeautifulSoup(driver.page_source,'lxml')
            # title = soup2.select_one('div.book-head div.cont span.h1').text
            try:
                title = soup2.find('span',class_='h1').text
                print("a")
            except Exception as e: #403 for this book
                print('errorrrr:',e)
                continue
            # author = soup2.select_one('div.book-head div.cont span.h2').text
            author = soup2.find('span',class_='h2').text
            print("b")
            try:
                status=soup2.find('a',class_='blue').text
                if status=='完本小说':
                    status='completed'
                elif status=='连载中':
                    status='ongoing'
            except:
                status="N/A"
            print("c")

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
            if len(chapter_times)>0:
                approx_novel_start=find_right_date("start",start,chapter_times)
            else:
                approx_novel_start="N/A"
            print("e")
            if len(chapter_times)>0:
                last_chapter_time=find_right_date("last",approx_num_chapts-1,chapter_times)
            else:
                last_chapter_time="N/A"
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
            time.sleep(3)
            try:
                WebDriverWait(driver,6).until(lambda x: x.find_element(By.CSS_SELECTOR,'#uv_info').is_displayed())
                # time.sleep(0.2)
                reads=driver.find_element(By.CSS_SELECTOR,'#uv_info').text
            except Exception as e:
                print("eerroorr:",e)
                reads="N/A"
            print("i")
            try:
                WebDriverWait(driver,6).until(lambda x: x.find_element(By.CSS_SELECTOR,'#recomment_total_info').is_displayed())
                # time.sleep(0.2)
                total_recomendations=driver.find_element(By.CSS_SELECTOR,'#recomment_total_info').text
            except Exception as e:
                print("eerroorr:",e)
                total_recomendations="N/A"
            print("j")
            try:
                WebDriverWait(driver,6).until(lambda x: x.find_element(By.CSS_SELECTOR,'#recomment_week_info').is_displayed())
                # time.sleep(0.2)
                weekly_recomendations=driver.find_element(By.CSS_SELECTOR,'#recomment_week_info').text
            except Exception as e:
                print("eerroorr:",e)
                weekly_recomendations="N/A"
            print("k")
            # other_url = f'https://www.4yt.net/ck/book/{book_id}/databox?appKey=3156022953'
            # attempts=0
            # # driver.get(other_url) #same book other page opened
            # while(True):
            #     try:
            #         attempts+=1
            #         response=requests.request("GET",other_url,headers=headers,timeout=60)
            #         request_no+=1
            #         # if request_no%150==0:
            #         #     print('sleeping for 30 secs..')
            #         #     time.sleep(30)
            #         if len(response.text)==0 or response.status_code!=200:
            #             raise Exception("api call empty response")
            #         # print(response.text)
            #         res_json =json.loads(response.text)
            #         reads = res_json['data']['pv']
            #         print("i")
            #         total_recomendations = res_json['data']['recommentTicket']
            #         print("j")
            #         weekly_recomendations = res_json['data']['week']['recommentTicket']
            #         print("k")
            #         break
            #     except Exception as e:
            #         print("attempt:",attempts)
            #         print("eeeeer:",e)
            #         if attempts<3:
            #             print("retrying in 5 secs..")
            #             time.sleep(5)
            #         else:
            #             reads="N/A"
            #             total_recomendations="N/A"
            #             weekly_recomendations="N/A"
            #             break
            print('book done')
            if reads=="" or reads=="-":
                reads="N/A"
            if total_recomendations=="" or total_recomendations=="-":
                total_recomendations="N/A"
            if weekly_recomendations=="" or weekly_recomendations=="-":
                weekly_recomendations="N/A"
            ans.loc[len(ans.index)]=[title,book_id,author,tags,approx_num_chapts,status,approx_novel_start,last_chapter_time,words,book_link,reads,total_recomendations,weekly_recomendations]
            ans.to_csv('4yt.csv',index=False)

        print("page done:",page_no)
        page_no+=1
    except Exception as e:
        print("err:",e)
        pass