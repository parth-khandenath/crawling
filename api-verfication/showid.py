import requests
import json
import time
import pandas as pd

def safe_get(dictionary, key, default=None):
    try:
        return dictionary[key]
    except (KeyError, TypeError):
        return default
    
headers = {
  'authority': 'api.cms.pocketfm.com',
  'accept': 'application/json, text/plain, */*',
  'accept-language': 'en-US,en;q=0.9',
  'access-token': 'a4792582dc97441fe3e7a56dd337866731a8b2c5',
  'app-client': 'consumer-web',
  'app-version': '180',
  'auth-token': 'web-auth',
  'cache-control': 'no-cache',
  'content-type': 'application/json',
  'origin': 'https://cms.pocketfm.in',
  'pragma': 'no-cache',
  'referer': 'https://cms.pocketfm.in/',
  'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"macOS"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'cross-site',
  'uid': 'edaae76a698ece0f207a3a346f6e5033cea1101f',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

# head2 = {'Show ID':[],'title':[],'Description':[],'Author':[],'VOA':[],'Production House':[],'Language':[],'type':[],'Category Type':[],
#          'Show source Genre':[],'Show sub source Genre':[],'tags':[],'Source of show':[],'Source Show Category':[],'License Date':[],'Origin name':[],
#          'Maturity':[],'Gender Pref':[],'Locking Episode':[],'Moderation':[],'AI':[]} 
head2={"show id":[],"name":[],"type":[], "lang":[]}
request_no=0
skipped_show=0
# leng = [ 'hindi']  #change here
leng = [ 'english']  #change here
for i in range(0,len(leng)):
    try:
        ans=pd.read_csv(f'{leng[i]}.csv')
    except:
        print("creating new dataframe...")
        ans = pd.DataFrame(head2)
    print(leng[i])
   
    # page_no = 17   #change
    page_no = 467   #change

    while True:
        try:
            url = f'https://api.cms.pocketfm.com/v2/content_api/book.published_shows?language={leng[i]}&page_no={page_no}&view=cms'
            print("page:",page_no)
            response = requests.get(url , headers=headers,timeout=60)
            request_no+=1
            if request_no%10==0:
                time.sleep(5)
            if response.status_code==404:
                print("last page reached...")
                print(leng[i],page_no)
                break
            try:
                data = json.loads(response.text)
            except Exception as e:
                print("json data load error:",e)
                print("retrying..")
                try:
                    time.sleep(5)
                    response = requests.get(url , headers=headers,timeout=60)
                    request_no+=1
                    if request_no%10==0:
                        time.sleep(5)
                    data = json.loads(response.text)
                except Exception as e:
                    print("error2 :",e)
                    break
            print(len(data["result"]["books"]))
            if len(data["result"]["books"]) == 0:
                print(f"no books on page {page_no}, breaking...")
                break
            page_no += 1
            for show in data["result"]["books"]:
                print("show id:",show['show_id'])
                response_book = requests.get(f'https://api.cms.pocketfm.com/v2/content_api/show.get_details?show_id={show["show_id"]}&info_level=min&curr_epoch=1690982603&is_novel=0',timeout=60)
                request_no+=1
                if request_no%10==0:
                    time.sleep(5)
                try:
                    book = json.loads(response_book.text)['result'][0]
                except Exception as e:
                    print("json data load error 2:",e)
                show_type = safe_get(book,'show_type',"field missing in API response")
                show_name = safe_get(book,'show_title',"field missing in API response")
                language=leng[i]
                show_id=show['show_id']
                
                ans.loc[len(ans.index)] = [show_id,show_name,show_type,language]
                ans.to_csv(f'{leng[i]}.csv',index=False)
        except ConnectionResetError:
            print("re-establishing reset connection in 20 secs..")
            time.sleep(20)
        except ConnectionAbortedError:
            print("re-establishing aborted connection in 20 secs..")
            time.sleep(20)
        except Exception as e:
            print("error:",e)
            print("re-trying connection in 20 secs..")
            time.sleep(20)
            # print("error:",e)
            # break