import time
import pandas as pd
import requests
import json
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium import webdriver 
# from DrissionPage import ChromiumPage
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# https://www.douyin.com/user/MS4wLjABAAAAWAenWc0G6yGqY2mGZHiIAdjrG0h1fowm-H3rlSm-6H4
headers = {
  'authority': 'www.douyin.com',
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
#   'cookie': 'ttwid=1%7C1Kpi68A9DIjJAgGe1R8dhIK1NvaKM3SX6Fwxz7BaoMg%7C1709539254%7C0d5bea5e6628284445d164038dd4a224b003423eb0b800ab9567c2f2ac3c34fc; dy_swidth=1536; dy_sheight=864; ttcid=33b988c82ea045a182bef3497fe9a31d14; passport_csrf_token=cef74790e76aeee418245bc829cd1c55; passport_csrf_token_default=cef74790e76aeee418245bc829cd1c55; bd_ticket_guard_client_web_domain=2; pwa2=%220%7C0%7C3%7C0%22; download_guide=%223%2F20240304%2F0%22; s_v_web_id=verify_ltctfpod_f61cadca_4072_f4b1_d288_045851754fd4; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%2C%22isForcePopClose%22%3A1%7D; volume_info=%7B%22isUserMute%22%3Afalse%2C%22isMute%22%3Atrue%2C%22volume%22%3A0.822%7D; csrf_session_id=199ffeb5a76cf45e4b9d19e546825ca8; strategyABtestKey=%221709789343.197%22; __ac_nonce=065e9bfce006b8f4c75c5; __ac_signature=_02B4Z6wo00f01AE61EwAAIDA.lZK33B96bQBGtDAAGWtAc9Iq-u11DawY2JVrJMbTmmMR6DQDqFa7eHA4IeIShT7Cnay6QGEf4R37uL375xh6cb-odPWBlzo8F1INe2uy..Q3F0ohKmPga0T93; GlobalGuideTimes=%221709818164%7C0%22; IsDouyinActive=true; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1536%2C%5C%22screen_height%5C%22%3A864%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A5.55%2C%5C%22effective_type%5C%22%3A%5C%224g%5C%22%2C%5C%22round_trip_time%5C%22%3A200%7D%22; home_can_add_dy_2_desktop=%221%22; msToken=OhXpHsOD6eInL8OuZU9lbIYflbYxUcOpfzHeAYMvaMgbb3aVqyhNdvtfGgsx5WqLfAzPPw-fYCqLgE-vf_us4eqNPUPYb0FOxPkm2kjjPpyj5o8AZQxh3c7LEVC8Jq4=; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQ1cyTkduNkJlZDJMSGNNcjhQVVZ6VVNEWTh4L2xzUXlvdWpRUlF0YVo2dUI5N09RUHp3QW9vOTZpZnhvMDJBUzc2cXpUbnpCWW1yNFJBTitJT2t1VVU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; msToken=4Ja6YPFkzGGOfz6c68d_V9qW7shJViXjp8WZ0zoflyaWU-YGoy3bKzrw-RL8xCCjH9c1luJrUw79y5MJiIXj2AH5SBP-QwQ1jBZ4G-jhMZqio1_xDrVpBBl_kNfN-qw=; tt_scid=Lc1eHMJv3aY.I.A-Oy1.M.obyo24Qt9.bGb6vXjL-VVTn20T9V8v0LeGQizgYrDMad3c',
  'referer': 'https://www.douyin.com/user/MS4wLjABAAAAWAenWc0G6yGqY2mGZHiIAdjrG0h1fowm-H3rlSm-6H4',
  'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
  'sec_user_id'
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
}
df_header={
    'creator_link':[],
    'creator_name':[],
    'video_url':[],
    'video_source_url':[],
    'videolength':[],
    'likes':[],
    'comments':[],
    'stars':[],
    'shares':[],
    'title':[],
    'releasetime':[]
}
cdf_header={
    'creator_name':[],
    'creator_link':[],
    'creator_focus':[],
    'creator_fans':[],
    'creator_liked':[],
    'douyin_account_id':[],
    'no_of_works':[],
    'about_creator':[]
}
options = Options()
options.add_argument(f"--header={headers}")
driver = webdriver.Chrome(options=options)
# driver=ChromiumPage()

def process(num):
    try:
        num=str(num)
        if num[-1]=='万':
            num=int(float(num[:-1])*10000)
        return num
    except Exception as e:
        print(e)
        return 'NA'
    
def allzeroes(s):
    s=str(s)
    for i in s:
        if not (i in [':','0','.']):
            return False
    return True

def get_aweme_ids(creator_link):
    lst=[]
    try:
        creator_identifier=creator_link.split('/')[-1]
        url = f"https://www.douyin.com/aweme/v1/web/aweme/post/?device_platform=webapp&aid=6383&channel=channel_pc_web&sec_user_id={creator_identifier}&max_cursor=0&locate_query=false&show_live_replay_strategy=1&need_time_list=1&time_list_query=0&whale_cut_token=&cut_version=1&count=18&publish_video_strategy_type=2&pc_client_type=1&version_code=170400&version_name=17.4.0&cookie_enabled=true&screen_width=1536&screen_height=864&browser_language=en-GB&browser_platform=Win32&browser_name=Chrome&browser_version=122.0.0.0&browser_online=true&engine_name=Blink&engine_version=122.0.0.0&os_name=Windows&os_version=10&cpu_core_num=8&device_memory=8&platform=PC&downlink=0.8&effective_type=3g&round_trip_time=400&webid=7342415126878422547&msToken=eZvS12-qeYnMRL7v59LRxxa5R3k7WCpkZSP-t70HB-3w7g6VgOVSWMXWVyvA8kPHYlsaH5Hz5J4LIJth_JFPiLz-5i-8KhiQxnbZhAjOBC39tWCI9eZzLYo7snfyrg==&X-Bogus=DFSzswVO3MvANVbotbh44/sZrJNv"

        payload = {}
        headers = {
        'authority': 'www.douyin.com',
        'accept': 'application/json, text/plain, */*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': '__ac_nonce=065e57fb500e95b7c728d; __ac_signature=_02B4Z6wo00f01YV7HSQAAIDBeheDtNMLOSWFWxmAAAS8c3; ttwid=1%7C1Kpi68A9DIjJAgGe1R8dhIK1NvaKM3SX6Fwxz7BaoMg%7C1709539254%7C0d5bea5e6628284445d164038dd4a224b003423eb0b800ab9567c2f2ac3c34fc; dy_swidth=1536; dy_sheight=864; strategyABtestKey=%221709539351.826%22; csrf_session_id=99b50f6e0edc70263ad45a69db8760a2; FORCE_LOGIN=%7B%22videoConsumedRemainSeconds%22%3A180%7D; ttcid=33b988c82ea045a182bef3497fe9a31d14; passport_csrf_token=cef74790e76aeee418245bc829cd1c55; passport_csrf_token_default=cef74790e76aeee418245bc829cd1c55; tt_scid=R72pviMP.7WGFia2CwFaiCRdBIWljZy5B8Tf5D-mFMPBDvw8FfLOeEA6xY2F-9Vz6810; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtcmVlLXB1YmxpYy1rZXkiOiJCQ1cyTkduNkJlZDJMSGNNcjhQVVZ6VVNEWTh4L2xzUXlvdWpRUlF0YVo2dUI5N09RUHp3QW9vOTZpZnhvMDJBUzc2cXpUbnpCWW1yNFJBTitJT2t1VVU9IiwiYmQtdGlja2V0LWd1YXJkLXdlYi12ZXJzaW9uIjoxfQ%3D%3D; bd_ticket_guard_client_web_domain=2; pwa2=%220%7C0%7C1%7C0%22; msToken=rbrK8Wua4qQ7BMTpN2PPqYD2blaTQlVPBUcwrHLQOe1_5U-d0Vq1XrkKQUOlDpNa6zLcd4iG4ZlmF_wwghzl01iOYu52ylvnGDozTqfwNTo4ToK4MT7K; download_guide=%221%2F20240304%2F0%22; IsDouyinActive=true; home_can_add_dy_2_desktop=%220%22; stream_recommend_feed_params=%22%7B%5C%22cookie_enabled%5C%22%3Atrue%2C%5C%22screen_width%5C%22%3A1536%2C%5C%22screen_height%5C%22%3A864%2C%5C%22browser_online%5C%22%3Atrue%2C%5C%22cpu_core_num%5C%22%3A8%2C%5C%22device_memory%5C%22%3A8%2C%5C%22downlink%5C%22%3A0.8%2C%5C%22effective_type%5C%22%3A%5C%223g%5C%22%2C%5C%22round_trip_time%5C%22%3A400%7D%22; msToken=eZvS12-qeYnMRL7v59LRxxa5R3k7WCpkZSP-t70HB-3w7g6VgOVSWMXWVyvA8kPHYlsaH5Hz5J4LIJth_JFPiLz-5i-8KhiQxnbZhAjOBC39tWCI9eZzLYo7snfyrg==',
        'referer': f'https://www.douyin.com/user/{creator_identifier}',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        }

        response = requests.request("GET", url, headers=headers, data=payload)
        res_json = response.json()
        for obj in res_json['aweme_list']:
            lst.append(obj['aweme_id'])
    except Exception as e:
        print(e)
    return lst

#getting creator links
creatorlinkfile="Douyin Creators List 2 - Sheet1.csv"  #change here
inputdf=pd.read_csv(creatorlinkfile)
creator_links=[]
for idx,row in inputdf.iterrows():
    link=row['Creator ID Link']
    if '?' in link:
        link=link.split('?')[0]
    creator_links.append(link)

videofilename="douyin-videos.csv"   #change here
cfilename="douyin-creators.csv"     #change here
try:
    df=pd.read_csv(videofilename)
except:
    df=pd.DataFrame(df_header) 

try:
    cdf=pd.read_csv(cfilename)
except:
    cdf=pd.DataFrame(cdf_header)
canskip=True
# creator_links=['https://www.douyin.com/user/MS4wLjABAAAAsC0iSmqSGjbTbl3iv3PruaZWtgIA59O87ks-4zkVHI6KtlaeY7A8Q88KicQGloAa']
for creator_link in creator_links:
    print('creator:',creator_link)
    if creator_link=='https://www.douyin.com/user/MS4wLjABAAAArSyDm6uGJ7vN7YNWjgbUFFmph2IO-MYqGVWsX4nTuKE':
        canskip=False
    if canskip:
        continue
    driver.get(creator_link)
    time.sleep(10)
    try:  #if captcha 
        ele=driver.find_element(By.CSS_SELECTOR,'.middle_page_loading')
        # ele = driver.ele('css:.middle_page_loading')  #drissionpage
        print('###############')
        print('SOLVE CAPTCHA')
        print('###############')
        time.sleep(30)
    except Exception as e:
        print(e)
    time.sleep(7)
    try:  #close qr panel
        ele=driver.find_element(By.CSS_SELECTOR,'div.bigqr')
        # ele=driver.ele('css:div.bigqr')   #drissionpage
        ele2=driver.find_element(By.CSS_SELECTOR,'div.dy-account-close')
        # ele2=driver.ele('css:div.dy-account-close')   #drissionpage
        ele2.click()
    except Exception as er:
        print(er)
    st=4
    while(st>0):
        driver.execute_script("window.scrollTo(0, window.scrollY+6000)")
        # driver.scroll('bottom',6000)   #drissionpage
        time.sleep(3)
        st-=1
    soup = BeautifulSoup(driver.page_source,"lxml")
    # soup = BeautifulSoup(driver.html,"lxml")  #drissionpage
    creatorname=soup.select_one('.a34DMvQe').text
    stat_eles=soup.select('.sCnO6dhe')
    creatorfocus=stat_eles[0].text
    creatorfocus=process(creatorfocus)   
    creatorfans=stat_eles[1].text   
    creatorfans=process(creatorfans)   
    creatorliked=stat_eles[2].text   
    creatorliked=process(creatorliked)   
    account_id=soup.select_one('.TVGQz3SI').text
    # account_id=account_info_eles[1]
    numofwork=soup.select_one('.PCbKMDUa').text
    numofwork=process(numofwork)
    try:
        aboutcreator=soup.select_one('.DtlymgqL span.j5WZzJdp').text
    except:
        aboutcreator="NA"
    # cdf.loc[len(cdf.index)]=[creatorname,creator_link,creatorfocus,creatorfans,creatorliked,account_id,numofwork,aboutcreator]
    # cdf.to_csv(cfilename,index=False)

    links=soup.select('.hY8lWHgA.SF0P5HVG.h0CXDpkg')
    links2=[]
    for link in links:
        links2.append('https://www.douyin.com'+link.get('href'))
    print(f'{len(links2)} videos')

    for videourl in links2:
        print('video:',videourl)
        try:
            driver.get(videourl)
            time.sleep(6)   
            soup2 = BeautifulSoup(driver.page_source,"lxml")
            # soup2 = BeautifulSoup(driver.html,"lxml") #drissionpage
            try:
                videolength=soup2.select_one('span.time-duration').text  #keep time.sleep high enough so that videolength is not 00:00
            except:
                time.sleep(6)
                soup2 = BeautifulSoup(driver.page_source,"lxml")
                # soup2 = BeautifulSoup(driver.html,"lxml") #drissionpage
                videolength=soup2.select_one('span.time-duration').text
            if allzeroes(videolength):
                time.sleep(6)
                soup2 = BeautifulSoup(driver.page_source,"lxml")
                # soup2 = BeautifulSoup(driver.html,"lxml") #drissionpage
                videolength=soup2.select_one('span.time-duration').text
            videolength=videolength.replace(':','m')
            video_source_url=soup2.select_one('video source').get('src')
            videolength+='s'
            print(videolength)
            stat_eles=soup2.select('.ofo4bP_8')
            likes=stat_eles[0].text
            if likes=='赞':  #thumbs up
                likes=0
            else:
                likes=process(likes)
            comments=stat_eles[1].text
            if comments=='抢首评': #be the first one to comment
                comments=0
            else:
                comments=process(comments)
            stars=stat_eles[2].text
            if stars=='收藏': #collect
                stars=0
            else:
                stars=process(stars)
            shares=soup2.select_one('.njfMvuRG').text
            if shares=='分享': #share
                shares=0
            else:
                shares=process(shares)
            title=soup2.select_one('h1.hE8dATZQ').text
            releasetime=soup2.select_one('.D8UdT9V8').text
            # releasetime=releasetime.split(':')[1]

            df.loc[len(df.index)]=[creator_link,creatorname,videourl,video_source_url,videolength,likes,comments,stars,shares,title,releasetime]
            df.to_csv(videofilename,index=False)
        except:
            pass