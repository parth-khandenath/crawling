import requests
import pandas as pd
import time

# sheet=pd.read_csv('Webnovel Comments Crawling.csv')
titles=[
"Young master Damiens pet",
"The Crowns Obsession",
"SPELLBOUND",
"Bambi and the Duke",
"Valerian Empire",
"Letters to Romeo.",
"Heidi and the Lord",
"Belle Adams Butler",
"My Dad Is the Galaxys Prince Charming",
"Hells Consort",
"Eternity in the darkness",
"Forced Bride Of The Vampire Lord",
"The Dukes Passion",
"Kiss Me Not",
"The Vampire Kings Possession",
]
bul=[
# 'https://www.webnovel.com/book/12700758805688005',
# 'https://www.webnovel.com/book/17319692206490105',
# 'https://www.webnovel.com/book/19724198606199605',
# 'https://www.webnovel.com/book/12005787806740405',
# 'https://www.webnovel.com/book/11972914206680405',
'https://www.webnovel.com/book/20198216906075605',
'https://www.webnovel.com/book/12005484305744805',
'https://www.webnovel.com/book/16699909406011105',
'https://www.webnovel.com/book/8896645106001105',
'https://www.webnovel.com/book/17597533305709905',
'https://www.webnovel.com/book/12163368005019905',
'https://www.webnovel.com/book/22244643905115305',
'https://www.webnovel.com/book/19548020106739705',
'https://www.webnovel.com/book/19834280805389505',
'https://www.webnovel.com/book/24356530305841205',
]
for i,book_url in enumerate(bul):
    time.sleep(10)
    skip=True
    # for idx,row in sheet.iterrows():
    # book_url= "https://www.webnovel.com/book/25392203506078605"  #row['URL']   #change herehttps://www.webnovel.com/book/the-alpha-claiming-his-enemy's-daughter_25392203506078605
    book_num_id=book_url.split('/')[-1]
    # if book_num_id=='16699683105884505':   
    #     skip=False
    # if skip:
    #     continue
    page_index=1
    cookie='2d145ea1-113c-4967-9ab8-d4ea1242587a'
    try:
        df=pd.read_csv(f'webnovel-comments-{book_num_id}.csv')
    except:
        df_header={ 'userName':[], 'rating':[], 'content':[], 'date':[] ,'likes':[], 'numReplies':[]}
        df=pd.DataFrame(df_header)
    headers = {
            'authority': 'www.webnovel.com',
            'accept': 'application/json, text/javascript, */*; q=0.01',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cookie': f'_csrfToken={cookie}; webnovel_uuid=1706524958_795298024; webnovel-content-language=en; webnovel-language=en; AMP_TOKEN=%24NOT_FOUND; _gid=GA1.2.812510157.1706524962; _fbp=fb.1.1706524963042.962545816; dontneedgoogleonetap=1; _gat=1; _ga=GA1.1.2099221000.1706524962; _ga_PH6KHFG28N=GS1.1.1706524962.1.1.1706525065.47.0.0',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
            }
    can_break=False
    while True:
        if can_break:
            print('breaking premature...')
            break
        time.sleep(1)
        response= requests.request('GET',f'https://www.webnovel.com/go/pcm/bookReview/get-reviews?_csrfToken={cookie}&bookId={book_num_id}&pageIndex={page_index}&pageSize=100&orderBy=1&novelType=0&needSummary=1&_=1706525066304',headers=headers)
        print(f'trying book id:{book_num_id}, page indx:{page_index}')
        res_json=response.json()
        data=res_json['data']
        reviews=data.get('bookReviewInfos')
        if not reviews or len(reviews)==0:
            print('no more reviews.....')
            break
        for review in reviews:
            userName=review['userName']
            rating=review['totalScore']
            content=review['content']
            date=review['createTimeFormat']
            likes=review['likeAmount']
            numReplies=review['replyAmount']
            if likes==0 and numReplies==0 and page_index>=100:
                can_break=True
            df.loc[len(df.index)]=[userName,rating,content,date,likes,numReplies]
            df.to_csv(f'webnovel-{titles[i]}-{book_num_id}.csv',index=False)
        page_index+=1

