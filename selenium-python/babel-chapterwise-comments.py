import json
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import time
import pandas as pd

booklinks=[
    'https://babelnovel.com/books/best-soldier-son-in-law','https://babelnovel.com/books/you-ceo-s-secret-wife'
]

chrome_options = uc.ChromeOptions()
# chrome_options.add_argument('--headless')
chrome_options.add_argument("--authority=api.babelnovel.com")
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("--cookie=_gcl_au=1.1.1914344749.1705391269; _fbp=fb.1.1705391270100.527150223; _gid=GA1.2.1973026431.1706096729; cf_clearance=SB3oR8CM3MBWP97.DYFGiz9Zc.jHFJI.uBH3BG3LMZQ-1706160274-1-AXfQOtnv2NFMsc740+rtp6Hh6O8bCtCucof0ETtnJgaqYymttQGDBhV4+oN0mcOA6V40M+9ObXuBPtC3V1e4d9Y=; _ga=GA1.2.1495954902.1705391269; _uetsid=13006440baae11ee95996bd51480a4e4; _uetvid=8feddb00b44311ee89e9fdb80d6593fd; ajs_anonymous_id=%2200311626-8b61-4d54-b1e2-f4ed4abdfcf4%22; __gads=ID=847ac9005391bf53:T=1705391291:RT=1706160295:S=ALNI_MaQDepY6rvWM2ZOEJqGmuXtVHIjPw; __gpi=UID=00000cdf2739b9f7:T=1705391291:RT=1706160295:S=ALNI_MZCx5nSivhcie68VPTiOGXYUz5egw; _ga_0Z0KQGSTHR=GS1.1.1706159884.3.1.1706161743.0.0.0")
chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
driver = uc.Chrome(options=chrome_options)

driver.get('https://babelnovel.com/')
time.sleep(6)
for bl in booklinks:
    bookid=bl.split('/')[-1]
    print(bl)
    try:
        df=pd.read_csv(f'babel-chapterwise-{bookid}.csv')
    except:
        df_header={'chapter':[], 'user':[],'content':[],'time':[],'likes':[],'replies':[]}
        df=pd.DataFrame(df_header)
    chno=1
    while(True):
        if chno>20:
            break
        print("chp: ",chno)
        url=f"https://api.babelnovel.com/v1/books/{bookid}/chapters/c{str(chno)}/discussion-fast"
        driver.get(url)
        time.sleep(1)
        soup=BeautifulSoup(driver.page_source,'lxml')
        response=json.loads(soup.text)
        if not response.get('data'):
            continue
        if not response['data'].get('comments'):
            continue
        for cmt in response['data']['comments']:
            df.loc[len(df.index)]=[chno,cmt['name'],cmt['cooked'],cmt['created_at'],cmt['like_count'],cmt['reply_count']]
            df.to_csv(f'babel-chapterwise-{bookid}.csv',index=False)
        chno+=1
        # url=f"https://api.babelnovel.com/v1/books/beauty-protecting-soldier-king/chapters/c2/discussion-fast"