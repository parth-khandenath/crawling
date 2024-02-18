import pandas as pd
import requests
import time

file='kakao-webtoon.csv'
sheet=pd.read_csv(file)
c=0
skip=True
for idx,row in sheet.iterrows():
    print(idx)
    id=row['id']
    id=id.split('-')[1]
    if id=='2087':
        skip=False
    if skip:
        continue
    url=f'https://gateway-kw.kakao.com/episode/v2/views/content-home/contents/{id}/episodes?sort=-NO&offset=0&limit=30'
    headers = {
            'authority': 'gateway-kw.kakao.com',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ko',
            'cookie': '_kpdid=09c1e5784fc6478994c04ff04c092e5b; _kpiid=bb367fa490bc82b7fd585f1b1b782703; _kadu=8BVOmyKYYpjOcGXQ_1704343293676; theme=dark; _kp_collector=KP.3310808493.1707890282561; _gcl_au=1.1.567674066.1707890283; _gid=GA1.2.198880558.1707890284; _fbp=fb.1.1707890284840.685466663; _ga=GA1.2.1891870976.1707890284; _ga_GLWD7GS60Q=GS1.2.1708096684.13.0.1708096684.60.0.0; _T_ANO=dZMh2BO1OdQrxx/uGwqxJk7baPEPGUHCeuhVuawbDfftYE3suPoUKogI7uHkwNshkeK262UxeOM0T1kHcCUPQX7MBZ1paOLGEajMg7vqcWvxSneaEImTfJnlghspc6pMqxXHJqxzunueQRIn0VUoYVgWnZ2jXsrfo4V1gnmbmP3fuCXFFRWSPAA+YI40eg0gH28iFKoSHgOFLXI5TCGmhGkv5+fk8yXlDltKPHPQ7LD8aItxqhRcqx4W9vOlK7IYDTAqzo6avwLfrZpSxDQdvJB0v8HQIF3r3t19k+EaDkXMot08ye1h61KcluKwgr33fIvNLSZmGU8LsrXfw810fA==; _ga_80D69HE0QD=GS1.1.1708096680.16.1.1708097464.0.0.0',
            'origin': 'https://webtoon.kakao.com',
            'referer': 'https://webtoon.kakao.com/',
            'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
        }
    response= requests.get(url, headers=headers, timeout=60)
    c+=1
    if c%40==0:
        time.sleep(10)
    resj=response.json()
    print(resj)
    sheet.at[idx, 'total_episodes'] = resj['meta']['pagination']['totalCount']
    sheet.to_csv(file,index=False)

