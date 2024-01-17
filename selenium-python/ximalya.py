import requests
import pandas as pd
import time
from selenium.webdriver.common.by import By
import undetected_chromedriver as uc

# album_ids=['47517749','18420226','29316562','3888524','76612906','18445821','4756811','4756811'] #change here       
album_ids=[]
id_df=pd.read_csv('xim-15jan/links-to-crawl.csv')
for idx,row in id_df.iterrows():
    alb_id=row['URL'].split('/')[-1]
    album_ids.append(alb_id)
print(len(album_ids))
print(album_ids)

df_header={
    'episode_title':[],
    'date':[],
    'duration':[],
    'playCount':[]
}
# options = uc.ChromeOptions() 
# options.page_load_strategy = 'eager'
# options.add_argument('--disable-blink-features=AutomationControlled')
# options.add_argument(f"--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36")

# driver = uc.Chrome(options=options)
c=0
for album_id in album_ids:
    c+=1
    if c<=34:
        continue
    try:
        df=pd.read_csv(f'xim-15jan/ximalya-{album_id}.csv')
    except:
        df=pd.DataFrame(df_header)
    headers = {
            "authority": "www.ximalaya.com",
            "accept": "*/*",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
            "cookie": "_xmLog=h5&630426cb-3ac8-4be5-bc43-2c171ac91f50&process.env.sdkVersion; Hm_lvt_4a7d8ec50cfd6af753c4f8aee3425070=1683016301; hide_himayala_bar=1; fds_otp=6222371113542586084; 1&remember_me=y; 1&_token=468425582&46FC7E60340NBC7334D34DF1C9B318AC0E42752F064776BB53D449D2B2B7389ED643330BE3B246MEE9155929A4647B_; login_type=code_mobile; xm-page-viewid=ximalaya-web; impl=www.ximalaya.com.login; x_xmly_traffic=utm_source%253A%2526utm_medium%253A%2526utm_campaign%253A%2526utm_content%253A%2526utm_term%253A%2526utm_from%253A; web_login=1683027908148",
            "referer": f"https://www.ximalaya.com/album/{album_id}",
            "sec-ch-ua": '"Chromium";v="112", "Google Chrome";v="112", "Not:A-Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Linux"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
            "xm-sign": "c03b9c71357310f0749d58ee60dd1343(75)1683027931132(76)1683027909330",
        }

    for page_no in range(1,11):
        print('page no:',page_no)
        url=f'https://www.ximalaya.com/revision/album/v1/getTracksList?albumId={album_id}&pageNum={page_no}&pageSize=100'
        response=requests.request('GET',url,headers=headers)
        res_json=response.json()
        tracks=res_json['data']['tracks']
        for track in tracks:
            # driver.get('https://www.ximalaya.com'+track['url'])
            # time.sleep(2)
            # date=driver.find_elements(By.CSS_SELECTOR,'.time')[0].text
            date=track['createDateFormat']
            df.loc[len(df.index)]=[track['title'],date,track['duration'],track['playCount']]
            df.to_csv(f'xim-15jan/ximalya-{album_id}.csv',index=False)

