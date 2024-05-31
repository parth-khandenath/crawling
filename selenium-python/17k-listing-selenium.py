import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup 
import re
import time
import pandas as pd
# 17k-493239
headers = {
            "title":[],
            "category": [],
            "book_id":[],
            "latest_chapter":[],
            "update_time": [],
            "author": [],
            "status": [],
            "URL": [],
            "tags": [],
            "Number of Readers":  [],
            "Number of Chapters": [],
            "Number of Words":  [],
            "Total Monthly Recommendation": []
        }

# ans = pd.DataFrame(headers)

options = uc.ChromeOptions() 
options.page_load_strategy = 'eager'
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
driver = uc.Chrome(options=options)

last_page=334 #change here
genders=['male', 'female']
gender_links=[ "https://www.17k.com/all/book/2_0_0_0_0_4_0_0", "https://www.17k.com/all/book/3_0_0_0_0_4_0_0"]
for ind in range(len(genders)):
    if genders[ind] == 'male':  #for skipping
        page_number = 293
    else:
        continue
        page_number=274 #updted 8:56 am 
    try:
        ans=pd.read_csv(f'17k-{genders[ind]}.csv')
    except:
        ans=pd.DataFrame(headers)
    while True:
        try:
            print("trying page:",page_number)
            if page_number>last_page:
                break
            catalog_link = f"{gender_links[ind]}_{page_number}.html"
            driver.get(catalog_link) #open a page of catalog
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source,'lxml')
            trs = soup.select("tbody tr")[1:]
            # print("###################")
            # print(len(trs))

            for tr in trs: #visit all books of this page
                try:
                    title = tr.select_one("a.jt").get_text(strip=True)
                    book_url2 = f"https:"+ tr.select_one("a.jt")["href"]
                    category = tr.select_one("td.td2").get_text(strip=True)
                    category = tr.select_one("td.td2 a").get_text(strip=True)
                    latest_chapter = tr.select_one("td.td4").get_text(strip=True)
                    update_time = tr.select_one("td.td7").get_text(strip=True)
                    author = tr.select_one("td.td6").get_text(strip=True)
                    state = tr.select_one("td.td8").get_text(strip=True)

                    driver.get(book_url2) #open book
                    # WebDriverWait(driver,6).until(lambda x: x.find_element(By.CSS_SELECTOR,'.amoutItem___1_NQS').is_displayed())
                    soup2 = BeautifulSoup(driver.page_source,'lxml')
                    try:
                        readers = soup2.select_one('em#howmuchreadBook').text
                    except:
                        print('reloading book')
                        driver.get(book_url2)
                        time.sleep(3)
                        soup2 = BeautifulSoup(driver.page_source,'lxml')
                    readers = soup2.select_one('em#howmuchreadBook').text
                    words = soup2.select_one('em.red').text
                    monthly_recomendations = soup2.select_one('td#flower_month').text
                    tag_eles=soup2.select('tr.label td a span')
                    tag_txts=[]
                    for ele in tag_eles:
                        tag_txts.append(ele.text)
                    tags = "-".join(tag_txts)
                    book_id=book_url2.split('/')[-1][:-5]
                    book_details_url = f"https://www.17k.com/list/{book_id}.html"

                    driver.get(book_details_url) #open book another page
                    soup3 = BeautifulSoup(driver.page_source,'lxml')
                    dls = soup3.select('dl.Volume')
                    num_chapters = 0
                    for dl in dls:
                        num_chapters += len(dl.select('span.ellipsis'))

                    # pattern = '^\d+'
                    # for part in book_url2.split('/')[::-1]:
                    #     if part!='':
                    #         match = re.match(pattern, part)
                    #         if match:
                    #             bookId=match[0]
                    #             break 
                    ans.loc[len(ans.index)]=[title,category,book_id,latest_chapter,update_time,author,state,book_url2,tags,readers,num_chapters,words,monthly_recomendations]
                    ans.to_csv(f'17k-{genders[ind]}.csv',index=False)
                except Exception as er:
                    print("errrrr:",er)
            page_number+=1
            break
        except Exception as e:
            print("err:",e)
            time.sleep(2)