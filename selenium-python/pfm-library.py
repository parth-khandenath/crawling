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
  'access-token': '2c114a38f03fe104242f750d264460ef2be8af35',
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
  'uid': 'f2fbd9eb40de572b3d80a9aa81afe94706e82a2a',
  'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

head2 = {'Show ID':[],'title':[],'Description':[],'Author':[],'VOA':[],'Production House':[],'Language':[],'type':[],'Category Type':[],
         'Show source Genre':[],'Show sub source Genre':[],'tags':[],'Source of show':[],'Source Show Category':[],'License Date':[],'Origin name':[],
         'Maturity':[],'Gender Pref':[],'Locking Episode':[],'Moderation':[],'AI':[]} 

request_no=0
skipped_show=0
leng = [ #'malayalam','telugu','tamil','kannada','marathi','bengali','spanish',
        'hindi','english']
for i in range(0,len(leng)):
    try:
        ans=pd.read_csv(f'PocketFm {leng[i]}.csv')
    except:
        ans = pd.DataFrame(head2)
    print(leng[i])
    url = f'https://api.cms.pocketfm.com/v2/content_api/book.published_shows?view=cms&language={leng[i]}&page_no=1&view=cms'
    page_no = 1
    # if leng[i]=='hindi':
    #     page_no=112
    while True:
        try:
            url = f'https://api.cms.pocketfm.com/v2/content_api/book.published_shows?view=cms&language={leng[i]}&page_no={page_no}&view=cms'
            print("page:",page_no)
            page_no += 1
            response = requests.get(url , headers=headers,timeout=60)
            if response.status_code==404:
                print("last page reached...")
                print(leng[i],page_no)
                break
            request_no+=1
            if request_no%10==0:
                time.sleep(5)
            data = json.loads(response.text)
            print(len(data["result"]["books"]))
            if len(data["result"]["books"]) == 0:
                break
            for show in data["result"]["books"]:
                print("show id:",show['show_id'])
                mod_res = requests.get(f'https://api.cms.pocketfm.com/v2/content_api/book.show_episodes?show_id={show["show_id"]}&view=cms&is_novel=0', headers=headers,timeout=60)
                request_no+=1
                if request_no%10==0:
                    time.sleep(5)
                response_book = requests.get(f'https://api.cms.pocketfm.com/v2/content_api/show.get_details?show_id={show["show_id"]}&info_level=min&curr_epoch=1690982603&is_novel=0',timeout=60)
                request_no+=1
                if request_no%10==0:
                    time.sleep(5)
                book = json.loads(response_book.text)['result'][0]
                show_type = safe_get(book,'show_type',{})
                if show_type !='series':
                    skipped_show+=1
                    print('not a series show',skipped_show)
                    continue
                tag_res = requests.get(f'https://api.cms.pocketfm.com/v2/content_api/tags.entity_tags?entity_id={show["show_id"]}&is_novel=0',headers=headers,timeout=60)
                request_no+=1
                if request_no%10==0:
                    time.sleep(5)
                VOA_res = requests.get(f'https://api.cms.pocketfm.com/v2/content_api/get_entity_cost?entity_id={show["show_id"]}',headers=headers,timeout=60)
                request_no+=1
                if request_no%10==0:
                    time.sleep(5)
                voaa = json.loads(VOA_res.text)
                tags = []
                if tag_res.status_code == 200:
                    tags_ = json.loads(tag_res.text)
                    tags = [i['tag_name'] for i in tags_['result']]
                tags = set(tags)
                show_id = show["show_id"]
                try:
                    show_desc = show["show_desc"]
                except Exception as e:
                    print(e)
                    try: 
                        show_desc=show["show_desc_html"]
                    except Exception as e2:
                        print(e2)
                        show_desc="error"
                title = safe_get(book,'show_title',{})
                author = safe_get(book, 'author_info', {}).get('fullname', '')
                try:
                    voa = voaa['result'][1]['name']
                except:
                    voa = '' 
                production_house = safe_get('production_house_info',book,{}).get('fullname','')
                language = safe_get(book, 'language', {})
                category_type = safe_get(book,'show_category',{})
                source_genre = safe_get(book,'show_genre_details',{}).get('topic_name','')
                source_sub_genre = safe_get(book,'show_sub_genre_details',{}).get('topic_name','')
                tags = str(list(tags))
                try:
                    source = safe_get(book, 'show_source', [''])[0]
                except:
                    source = ''
                source_show_category = safe_get(book,'source_show_category',{})
                license_date = safe_get(book,'license_date',{})
                show_origin_name = safe_get(book,'show_origin_name',{})
                maturity = safe_get(book,'maturity_rating',{})
                gender_pref = safe_get(book,'tags',{})
                locking_episode = safe_get(book,'is_episode_locking_allowed',{})
                try:
                    moderation = json.loads(mod_res.text)['result']['moderation_required']
                except:
                    moderation = ''
                ai = safe_get(book,'ai_show',{})
                if ai is None:
                    ai = "NO"
                else:
                    ai = "YES"
                
                # plays = safe_get(book, 'stats', {}).get('total_plays', 0)
                # duration = safe_get(book,'show_duration',{})
                # like = safe_get(book, 'stats', {}).get('like_count', 0)
                # rating = safe_get(book, 'stats', {}).get('avg_rating', 0)
                # rating_count = safe_get(book, 'stats', {}).get('rating_count', 0)
                # sub_count = safe_get(book, 'stats', {}).get('subscriber_count', 0)
                # published_episodes_count = safe_get(book, 'episodes_count', 0)
                # shares = safe_get(book, 'stats', {}).get('share_count', 0)
                # editor_score = safe_get(book, 'editor_score', 0)
                
                
                # if author == '':
                #     author = safe_get(book,'user_info',{}).get('fullname','')
                # book_type = safe_get(book, 'show_type', '')
                # category = safe_get(book, 'show_genre_details', {}).get('topic_name', '')
                # sub_genre = safe_get(book,'show_sub_genre_details').get('topic_name','')
                # status = safe_get(book, 'completed')
                # if status is True:
                #     status = 'completed'
                # else:
                #     status = 'running'
                
                ans.loc[len(ans.index)] = [show_id,title,show_desc,author,voa,production_house,language,show_type,category_type,source_genre,source_sub_genre,tags,source,
                 source_show_category,license_date,show_origin_name,maturity,gender_pref,locking_episode,moderation,ai]
                ans.to_csv(f'PocketFm {leng[i]}.csv',index=False)
        except ConnectionResetError:
            print("re-establishing connection in 20 secs..")
            time.sleep(20)
        except Exception as e:
            print("error:",e)
            break