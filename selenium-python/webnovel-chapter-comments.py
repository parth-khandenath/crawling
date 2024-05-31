import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup 
import requests,time
import pandas as pd

all_book_urls=[                                                 #change here
# ['https://www.webnovel.com/book/12700758805688005','Young master Damiens pet',37],
# ['https://www.webnovel.com/book/17319692206490105','The Crowns Obsession',36],
# ['https://www.webnovel.com/book/19724198606199605','SPELLBOUND',25],
# ['https://www.webnovel.com/book/12005787806740405','Bambi and the Duke',44],
# ['https://www.webnovel.com/book/11972914206680405','Valerian Empire',28],
# ['https://www.webnovel.com/book/20198216906075605','Letters to Romeo',30],
# ['https://www.webnovel.com/book/12005484305744805','Heidi and the Lord',29],
# ['https://www.webnovel.com/book/16699909406011105','Belle Adams Butler',49 ],   #here onwards
# ['https://www.webnovel.com/book/8896645106001105','My Dad Is the Galaxys Prince Charming',64],
['https://www.webnovel.com/book/17597533305709905','Hells Consort',37], 
['https://www.webnovel.com/book/12163368005019905','Eternity in the darkness',39],
# ['https://www.webnovel.com/book/22244643905115305','Forced Bride Of The Vampire Lord',43],
# ['https://www.webnovel.com/book/19548020106739705','The Dukes Passion',25],
# ['https://www.webnovel.com/book/19834280805389505','Kiss Me Not',40],
# ['https://www.webnovel.com/book/24356530305841205','The Vampire Kings Possession',25],
    ]
for _,l in enumerate(all_book_urls):
    time.sleep(8)
    book_url=l[0]
    book_id=book_url.split('/')[-1]
    options = uc.ChromeOptions() 
    # options.page_load_strategy = 'eager'
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
    driver = uc.Chrome(options=options)

    driver.get(book_url) #open book
    alt_link=driver.current_url  #redirected alternate link
    # print(alt_link)
    driver.get(alt_link+'/catalog') #open table of contents
    time.sleep(10)
    atags=driver.find_elements(By.CSS_SELECTOR,".db.pr")
    last_free_chapter=l[2]
    atags=atags[:last_free_chapter]  
    chpt_links=[]
    for a in atags:
        chpt_links.append(a.get_attribute("href"))

    driver.close()
    cookie='2d145ea1-113c-4967-9ab8-d4ea1242587a'
    headers = {
        'authority': 'www.webnovel.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': f'_csrfToken={cookie}; webnovel_uuid=1706954226_233238335; webnovel-content-language=en; webnovel-language=en; __gads=ID=6bd3c0e410b8411c:T=1706954232:RT=1706954232:S=ALNI_MYjrgBaDx4gLykecw5cVhvWTr1ZqQ; __gpi=UID=00000cf77316f3b3:T=1706954232:RT=1706954232:S=ALNI_MbU-D3IgddY86IDaVEY6ElOF9pUfg; __eoi=ID=4e95b22b447bfce4:T=1706954232:RT=1706954232:S=AA-AfjYmY0FHQpb6RkaSqHCuOJWS; AMP_TOKEN=%24NOT_FOUND; _gid=GA1.2.1491001713.1706954236; _fbp=fb.1.1706954236801.845173433; dontneedgoogleonetap=1; _gat=1; _ga_PH6KHFG28N=GS1.1.1706954234.1.1.1706954301.60.0.0; _ga=GA1.1.470036284.1706954232',
        'referer': 'https://www.webnovel.com/book/one-birth-two-treasures-the-billionaire\'s-sweet-love_11806186606531405/mistaken-identities_32400550196730452',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
        }
    c=0
    try:
        df=pd.read_csv(f'webnovel-chapterwise-comments-{book_id}.csv')
    except:
        df_header={ 'chapter':[], 'userName':[], 'content':[], 'date':[] ,'likes':[], 'numReplies':[]}
        df=pd.DataFrame(df_header)
    # print(atags)
    for chpt_link in chpt_links: #iterate over chapters
        time.sleep(2)
        c+=1
        chapter_id=chpt_link.split('_')[-1]
        print('chapter no:',c,' chpt id:',chapter_id)
        page_index=1
        can_break=False
        while True: #get all comments
            if can_break:
                print('breaking premature...')
                break
            print('page:',page_index)
            url = f"https://www.webnovel.com/go/pcm/chapterReview/getReviewList?_csrfToken={cookie}&bookId={book_id}&chapterId={chapter_id}&orderType=1&pageIndex={page_index}&_=1706954294806"
            response = requests.request("GET", url, headers=headers, timeout=60)
            response=response.json()
            reviews=response['data']['chapterReviewItems']
            if len(reviews)==0:
                    print('no more reviews.....')
                    break
            for review in reviews:
                userName=review['userName']
                content=review['content']
                date=review['createTimeFormat']
                likes=review['likeAmount']
                numReplies=review['replyAmount']
                if likes==0 and numReplies==0 and page_index>=25:
                    can_break=True
                df.loc[len(df.index)]=[c,userName,content,date,likes,numReplies]
                df.to_csv(f'webnovel-chapterwise-{l[1]}-{book_id}.csv',index=False)
            page_index+=1


# curl "https://www.webnovel.com/go/pcm/chapterReview/getReviewList?_csrfToken=f8b509d0-eb3c-4085-a4db-a9077e466293&bookId=11806186606531405&chapterId=32400550196730452&lastReviewId=0&orderType=1&pageIndex=1&_=1706954294806" ^
#   -H "authority: www.webnovel.com" ^
#   -H "accept: application/json, text/javascript, */*; q=0.01" ^
#   -H "accept-language: en-GB,en-US;q=0.9,en;q=0.8" ^
#   -H "cookie: _csrfToken=f8b509d0-eb3c-4085-a4db-a9077e466293; webnovel_uuid=1706954226_233238335; webnovel-content-language=en; webnovel-language=en; __gads=ID=6bd3c0e410b8411c:T=1706954232:RT=1706954232:S=ALNI_MYjrgBaDx4gLykecw5cVhvWTr1ZqQ; __gpi=UID=00000cf77316f3b3:T=1706954232:RT=1706954232:S=ALNI_MbU-D3IgddY86IDaVEY6ElOF9pUfg; __eoi=ID=4e95b22b447bfce4:T=1706954232:RT=1706954232:S=AA-AfjYmY0FHQpb6RkaSqHCuOJWS; AMP_TOKEN=^%^24NOT_FOUND; _gid=GA1.2.1491001713.1706954236; _fbp=fb.1.1706954236801.845173433; dontneedgoogleonetap=1; _gat=1; _ga_PH6KHFG28N=GS1.1.1706954234.1.1.1706954301.60.0.0; _ga=GA1.1.470036284.1706954232" ^
#   -H "referer: https://www.webnovel.com/book/one-birth-two-treasures-the-billionaire's-sweet-love_11806186606531405/mistaken-identities_32400550196730452" ^
#   -H "sec-ch-ua: ^\^"Not A(Brand^\^";v=^\^"99^\^", ^\^"Google Chrome^\^";v=^\^"121^\^", ^\^"Chromium^\^";v=^\^"121^\^"" ^
#   -H "sec-ch-ua-mobile: ?0" ^
#   -H "sec-ch-ua-platform: ^\^"Windows^\^"" ^
#   -H "sec-fetch-dest: empty" ^
#   -H "sec-fetch-mode: cors" ^
#   -H "sec-fetch-site: same-origin" ^
#   -H "user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36" ^
#   -H "x-requested-with: XMLHttpRequest" ^
#   --compressed