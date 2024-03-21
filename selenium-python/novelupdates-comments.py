import undetected_chromedriver as uc
import pandas as pd
import time
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
#  a#revname  -names
# .w-comments-item-text  -contents
# .rev_bar span  -likes
# td+ td div - even indices

header = {
    "name":[],
    "date":[],
    "content":[],
    "likes":[]
}
bookurl="https://www.novelupdates.com/series/hidden-marriage"  #change here
lastpage=11  #change here

bookid=bookurl.split('/')[-1]
try:
    df=pd.read_csv(f"novelupdates-comments-{bookid}.csv")
except:
    df=pd.DataFrame(header)

options = uc.ChromeOptions() 
options.page_load_strategy = 'eager'
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

driver = uc.Chrome(options=options)
page=1

while(True):
    if page>lastpage:
        break
    url=f"{bookurl}/comment-page-{str(page)}/#comments"
    driver.get(url)
    time.sleep(10)
    print(page)
    soup=BeautifulSoup(driver.page_source,'lxml')
    name_eles=soup.select('a#revname')
    content_eles=soup.select('.w-comments-item-text')   
    like_eles=soup.select('.rev_bar span')
    date_eles=soup.select('td+ td div')
    for i in range(len(name_eles)):
        name=name_eles[i].text
        content=content_eles[i].get_text(strip=True)
        likes=like_eles[i].text
        date=date_eles[2*i].text
        df.loc[len(df.index)]=[name,date,content,likes]
        df.to_csv(f"novelupdates-comments-{bookid}.csv",index=False)
    page+=1
