if __name__ =='__main__':
        
    import requests
    import json
    import pandas as pd

    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Origin': 'https://w2.heiyan.com',
        'Pragma': 'no-cache',
        'Referer': 'https://w2.heiyan.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Google Chrome";v="119", "Not;A=Brand";v="8", "Chromium";v="119"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    params = {
        'sort': '-1',
        'words': '-1',
        'free': '',
        'finish': '',
        'order': '3',
        'page': '1',
        'solicitingid': '0',
    }
    head = {
        "bookId":[],
        "Title":[],
        "URL" :[],
        "Tags":[],
        "Words_Total" : [],
        "Total_Clicks":[],
        "Monthly_Clicks":[],
        "weekly_clicks":[],
        "Finished":[],
        "Publish Time":[],
        "Last chapter/No. of chapters ":[]
    }

    ans = pd.DataFrame(head)


    while True:     
        print(params['page'])
        response = requests.get('https://search.heiyan.com/m/all', params=params, headers=headers)
        if response.status_code == 500:
            break
        novels = json.loads(response.text)['data']['content']
        for novel in novels:
            # print(novel)
            bookId = 'heiyan-'+str(novel['bookId'])
            title = novel['name']
            words = novel['words'] 
            tags = novel['tags']
            totalClicks = novel['totalpv']
            monthlyClicks = novel['monthpv']
            weeklyClicks = novel['weekpv']
            last_chapter = novel['lastchaptername']
            first_chapter_time = novel['publishtime']
            finished = novel['finished']
            URL = 'https://w2.heiyan.com/book/' + str(novel['id'])
            print(URL)
            ans.loc[len(ans.index)] = [str(bookId),str(title),str(URL),str(tags),str(words),str(totalClicks),str(monthlyClicks), str(weeklyClicks),str(finished),str(first_chapter_time),str(last_chapter)]
            ans.to_csv('heiyan.csv',index=False)
        params['page'] = str(int(params['page']) + 1)