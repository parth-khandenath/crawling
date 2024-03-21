import requests
import pandas as pd

# sheet=pd.read_csv('Webnovel Comments Crawling.csv')

skip=True
# for idx,row in sheet.iterrows():
book_url= "https://www.webnovel.com/book/6831850602000905"#row['URL']
book_num_id=book_url.split('/')[-1]
# if book_num_id=='16699683105884505':   
#     skip=False
# if skip:
#     continue
page_index=1
try:
    df=pd.read_csv(f'webnovel-comments-{book_num_id}.csv')
except:
    df_header={ 'userName':[], 'rating':[], 'content':[],  'date':[] ,'likes':[], 'numReplies':[]}
    df=pd.DataFrame(df_header)
headers = {
        'authority': 'www.webnovel.com',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': '_csrfToken=d6304992-5ad9-4854-be07-eed8bab19339; webnovel_uuid=1706524958_795298024; webnovel-content-language=en; webnovel-language=en; AMP_TOKEN=%24NOT_FOUND; _gid=GA1.2.812510157.1706524962; _fbp=fb.1.1706524963042.962545816; dontneedgoogleonetap=1; _gat=1; _ga=GA1.1.2099221000.1706524962; _ga_PH6KHFG28N=GS1.1.1706524962.1.1.1706525065.47.0.0',
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
    response= requests.request('GET',f'https://www.webnovel.com/go/pcm/bookReview/get-reviews?_csrfToken=d6304992-5ad9-4854-be07-eed8bab19339&bookId={book_num_id}&pageIndex={page_index}&pageSize=100&orderBy=1&novelType=0&needSummary=1&_=1706525066304',headers=headers)
    print(f'trying book id:{book_num_id}, page indx:{page_index}')
    res_json=response.json()
    data=res_json['data']
    reviews=data['bookReviewInfos']
    if len(reviews)==0:
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
        df.to_csv(f'webnovel-comments-{book_num_id}.csv',index=False)
    page_index+=1

