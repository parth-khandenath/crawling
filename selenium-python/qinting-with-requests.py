import requests
from bs4 import BeautifulSoup as bs
import pandas as pd
import json
import time

df_header = {"title":[],"url":[],"anchors":[],"description":[],"total plays":[],"episode count":[],"episode 1 plays":[],"episode 1 date":[]}
try:
    ans = pd.read_csv('qinting-suspense-supernatural.csv')  
except:
    ans = pd.DataFrame(df_header)

genre_code='3839' #change here, scroll for more changes
pg_no=(len(ans)//30) +1

while True:
    try:
        print('page no:',pg_no)
        main_url = f"https://webapi.qingting.fm/api/mobile/categories/521/attr/3289-{genre_code}/?page={pg_no}"
        payload = {}
        headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'Cache-Control': 'max-age=0',
        'Connection': 'keep-alive',
        'Cookie': 'HWWAFSESID=b7e7a737be5a8cb9e0; HWWAFSESTIME=1703073273454; INGRESSCOOKIE=1703073274.461.3351.108366; HWWAFSESID=40bf57f1284c17d700; HWWAFSESTIME=1703047235393',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"'
        }
        response = requests.request("GET", main_url, headers=headers, data=payload,timeout=120)
        # seq='3289-3842'
        # url = f'https://webapi.qingting.fm/api/mobile/categories/521/attr/{seq}/'  # Replace with the URL you want to scrape
        # response = requests.get(url,timeout=60)
        data = json.loads(response.text)
        if str(response.text) == '数据错误' or data["FilterList"] is None or response.status_code!=200: #data error
            print("Status code: ",response.status_code)
            print("Could not fetch!!")
            if data["FilterList"] is None:
                break
        else:
            # for entry in data["FilterList"]:
            i=0
            while i <(len(data["FilterList"])):
                entry=data['FilterList'][i]
                url1 = 'https://m.qingting.fm/vchannels/' + str(entry['id'])
                title = entry['title']
                episodes = entry['program_count']
                descr=entry['description']
                plays = entry['playcount']
                # try:
                #     resp = requests.get(url1,timeout=60)
                # except requests.exceptions.Timeout:
                #     try:
                #         time.sleep(10)
                #         resp = requests.get(url1,timeout=60)
                #     except requests.exceptions.Timeout:
                #         print('timeout')
                #     except requests.exceptions.ConnectionError:
                #         print('conection broken')
                url2 = 'https://webapi.qingting.fm/api/mobile/channels/' + str(entry['id'])
                url3 = url2 + '/programs?version='   
                # try:
                #     soup = bs(resp.content,'lxml')
                #     # tags = soup.select_one('.pods').text
                #     # first_name = soup.select_one('.single-line').text
                #     # first_time = soup.select_one('.time').text
                #     try:
                #         first_date = soup.select_one('.date font font').get_text(strip=True)
                #     except:
                #         first_date = "error"
                #     try:
                #         anchor=soup.select_one('.pods a font font').get_text(strip=True)
                #     except:
                #         anchor='error'
                # except Exception as e:
                #     # tags = "error"
                #     # first_name = "error"
                #     # first_time = "error"
                #     print(e)
                anchors=['error']
                first_ep_plays = 'error'
                first_ep_date = 'error'
                try:
                    respp = requests.get(url2,timeout=60)
                    respp_json=json.loads(respp.text)
                    try:
                        anchors=[]
                        for anchor in respp_json['channel']['podcasters']:
                            anchors.append(anchor['name'])
                    except:
                        anchors=['error']
                    print(url3 + respp_json['channel']['v'])
                    resp2 = requests.get(url3 + respp_json['channel']['v'],timeout=62)
                    resp2_json=json.loads(resp2.text)
                    try:
                        first_ep_plays = resp2_json['programs'][0]['playCount']
                        first_ep_date = resp2_json['programs'][0]['updateTime'][:10]
                    except:
                        first_ep_plays = 'error'
                        first_ep_date = 'error'
                except Exception as e:
                    print(e)
                ans.loc[len(ans.index)] = [title,url1,anchors,descr,plays,episodes,first_ep_plays,first_ep_date]
                ans.to_csv('qinting-fantasy-superpower.csv',index=False) #change here
                i+=1
        pg_no+=1
    except Exception as e: #all pages for this genre done
        print(e)
        if pg_no>83: #hardcoded last page for this genre
            break
