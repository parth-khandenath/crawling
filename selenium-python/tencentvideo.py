import requests
import json
import os
from csv import DictWriter
import time
import undetected_chromedriver as uc
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# file_name="tencentvideo-anime.csv"  #page 92 turned out to be the last page
# channelid='100119'
file_name="tencentvideo-TVdrama.csv"    #page x is the last page
channelid='100113'

df_header = {'bookId':[],
        'title':[],
        'url': [],
        'hotness': [],
        'region': [],
        'releaseYear': [],
        'tags': [],
        'totalEpisodes': [],
        'introduction': [] }

def get_payload(page):
    if page == 0:
        payload = json.dumps({
            "page_context": None,
            "page_params": {
                "page_id": str(channelid),
                "page_type": "channel",
                "skip_privacy_types": "0",
                "support_click_scan": "1",
                "new_mark_label_enabled": "1"
            },
            "page_bypass_params": {
                "params": {
                "caller_id": "3000010",
                "data_mode": "default",
                "page_id": str(channelid),
                "page_type": "channel",
                "platform_id": "2",
                "user_mode": "default"
                },
                "scene": "channel",
                "abtest_bypass_id": "7f3ccf505389bdc2"
            }
            })
    else:
        payload = json.dumps({
            "page_context": {
                "page_index": str(page)
            },
            "page_params": {
                "page_id": "channel_list_second_page",
                "page_type": "operation",
                "channel_id": str(channelid),
                "filter_params": "sort=75",
                "page": str(page),
                "new_mark_label_enabled": "1"
            },
            "page_bypass_params": {
                "params": {
                "page_id": "channel_list_second_page",
                "page_type": "operation",
                "channel_id": str(channelid),
                "filter_params": "sort=75",
                "page": str(page),
                "caller_id": "3000010",
                "platform_id": "2",
                "data_mode": "default",
                "user_mode": "default"
                },
                "scene": "operation",
                "abtest_bypass_id": "7f3ccf505389bdc2"
            }
            })
    return payload


url = "https://pbaccess.video.qq.com/trpc.vector_layout.page_view.PageService/getPage?video_appid=3000010"


headers = {
  'authority': 'pbaccess.video.qq.com',
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'content-type': 'application/json',
  'cookie': 'qq_domain_video_guid_verify=7f3ccf505389bdc2; _qimei_uuid42=183010e113a1002f9862363182dec709edd78e889d; _qimei_fingerprint=1c609ff4531c6a835b185cfa96d323f7; pgv_pvid=2097815516; video_platform=2; video_guid=7f3ccf505389bdc2; _qimei_q36=; _qimei_h38=2db878989862363182dec70902000001218301; pgv_info=ssid=s3417771617',
  'origin': 'https://v.qq.com',
  'referer': 'https://v.qq.com/',
  'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-site',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}

options = uc.ChromeOptions()
options.add_argument(f"--header={headers}")
driver = uc.Chrome(options=options)

def append_list_as_row(list_of_elem):
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
        writer = DictWriter(csvfile, fieldnames=df_header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(list_of_elem)

def get_book(booklink, id):
    attempts=6
    while attempts>0:
        try:
            driver.get(booklink)
            # time.sleep(6)
            break
        except WebDriverException:
            print("reloading",end=" ")
            attempts-=1
    if attempts==0:
        print('could not load')
        return
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source,'lxml')
    try:
        title = soup.select_one('.playlist-intro-new__title').text
    except:
        title='NA'
    try:
        hotness = soup.select_one('.svg-icon__fire+ span').text
    except:
        hotness='NA'
    try:
        span_eles = soup.select('span.playlist-intro-info__item')
        region = span_eles[0].text.split()[1]
        releaseyear = span_eles[1].text.split()[1]
        totalepisodes='NA'
        rest_lst = span_eles[2:]
        tags=[]
        for ele in rest_lst:
            if '全' in ele.text and '集' in ele.text:  #total episodes  #all/completed and episodes
                if '·' in ele.text:
                    totalepisodes = ele.text.split()[1]
                    totalepisodes = totalepisodes[1:-1]
                else:
                    totalepisodes = ele.text
            elif '集' in ele.text: #last updated episode   #episodes
                pass
            else:  #tags
                if '·' in ele.text:
                    tag = ele.text.split()[1]
                else:
                    tag = ele.text
                tags.append(tag)
    except:
        region='NA'
        releaseyear='NA'
        totalepisodes='NA'
        tags=[]

    try:
        driver.find_element(By.CSS_SELECTOR,'.playlist-intro-new__expand').click()
        time.sleep(0.6)
        intro = driver.find_element(By.CSS_SELECTOR,'.overlay-intro__desc').text
    except:
        intro='NA'

    data={
        'bookId':'tencentvideo-'+str(id),
        'title':title,
        'url': booklink,
        'hotness': hotness,
        'region': region,
        'releaseYear': releaseyear,
        'tags': tags,
        'totalEpisodes': totalepisodes,
        'introduction': intro
    }

    append_list_as_row(data)

# start=0
start=92
canskip=True
page=start   
while(True):
    if page==start:
        driver.get('https://www.google.co.in/')
        print('install urban vpn!! in 2 mins...')
        time.sleep(120)
    payload = get_payload(page)
    response = requests.request("POST", url, headers=headers, data=payload)
    if response.status_code!=200:
        break
    print('page: ',page)
    res_json = response.json()
    cardlist= res_json['data']['CardList']
    for obj in cardlist:
        if obj.get('children_list') and obj.get('children_list').get('list'):
            cards = obj.get('children_list').get('list').get('cards')
            for card in cards:
                cid = card['params'].get('cid')
                if cid:
                    book_link = f'https://v.qq.com/x/cover/{cid}.html'
                    print(book_link)
                    if book_link=='https://v.qq.com/x/cover/8rvudgp9wngcozf.html':
                        canskip=False
                    if canskip:
                        continue
                    get_book(book_link,cid)

    page += 1
