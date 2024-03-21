import scrapy
import pandas as pd
import json
import requests

class QuoteSpider(scrapy.Spider):
    name = 'wattpad23'
    start_urls = ['https://www.wattpad.com/list/'] 
    custom_settings={
        'CONCURRENT_REQUESTS':1
    }
    file_name=f'wattpad-originals' 
    category='' 
    all_cats=['featuredstories','newreleases','romance','werewolf','lgbt','newadult','diverselit','teenfiction','wattpadbooks','lessthan74coins','urbanfantasy','genreyoungadult','historicalfiction','paranormal','sciencefiction','vampire','series','fantasy','chicklit','sexyandsteamy','emotionalanduplifting','darkanddisturbing','mystery','horror','thriller','adventure','action','humor']
    sheet = 'wattpad_listing'
    Headers = {"genre":[],"title":[] , "book_url":[], "read_count":[] , "vote_count":[], "parts":[], "time (hrs.)":[], "author":[], "status":[], "mature_status":[], "description":[], "tags":[], "chapter1_publish_date":[],"book_id":[]}
    ans = pd.DataFrame(Headers)

    def parse(self,response):
        for cat in self.all_cats:
            self.category=cat
            url = f"https://www.wattpad.com/v4/paid_stories/tags/{self.category}?limit=-1&fields=stories(id,title,tags,length,voteCount,readCount,url,numParts,user,completed,description,firstPublishedPart,mature),tag"

            payload = {}
            headers = {
            'authority': 'www.wattpad.com',
            'accept': '*/*',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'authorization': 'IwKhVmNM7VXhnsVb0BabhS',
            'cookie': 'wp_id=ca8ae818-ec45-46f8-988f-8b7f0b744243; lang=1; locale=en_US; ff=1; dpr=1; tz=-5.5; X-Time-Zone=Asia%2FCalcutta; _col_uuid=b44b2218-c32d-47f0-8126-02961550cf8e-hv9s; _fbp=fb.1.1702271570875.1212863649; _gid=GA1.2.1991356261.1702271571; _pbjs_userid_consent_data=3524755945110770; _pubcid=cd9caa39-f24b-4a61-baca-079795eaf5a1; g_state={"i_p":1702288923789,"i_l":1}; fs__exp=5; te_session_id=1702360064630; wp-web-page=true; premiumPicksLists=%7B%22current%22%3A%5B%22294545538%22%2C%22297744774%22%2C%22302248068%22%2C%22257937611%22%2C%22180554942%22%2C%2284105002%22%2C%22124500284%22%2C%2220619442%22%5D%2C%22next%22%3A%5B%22155207768%22%2C%2211963741%22%2C%22137675320%22%2C%2212082636%22%2C%22107904993%22%5D%7D; nextUrl=%2Flist%2F1509052297-and-the-2023-watty-award-winners-are; token=455583260%3A2%3A1702362428%3Ay7QdX5G4ZhXK9ZfmYncm_-bbylNQk7aJNlkGf431KXykFM4XJy10xFwLbMOliyEO; isStaff=1; seen-wo-onboard=1; cto_bundle=odoe2l9GN2Q2SCUyQkIlMkZzYnVmajM3N2Y5MFlINzZNbTVaY3hnalBSdUZiY0VZaDI2aVhyYjlUU2swakF0aDZ2N1pybkpoVW5rNnB0WTBZSnY2b0hPWWxlWFB2SlRoSVR5aE9LWU9LTUtQSSUyRkJicE9IaGhoQmg5dmpEbUJMMUxFJTJCcmxuc25aV1R1NkVuVnNJNWw4MTV0Z2VjaTJCdyUzRCUzRA; AMP_TOKEN=%24NOT_FOUND; RT=; _ga=GA1.1.1488413246.1702271567; _ga_FNDTZ0MZDQ=GS1.1.1702371680.7.1.1702379238.0.0.0; lang=1; locale=en_US',
            'if-none-match': 'W/"f3aec1bfdbf1dcb3aca8f8abc2a3fa40debca31e"',
            'referer': 'https://www.wattpad.com/catalog/wattpadoriginals',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'x-requested-with': 'XMLHttpRequest'
            }

            books_response = requests.request("GET", url, headers=headers, data=payload)


            if books_response.status_code==200:
                    response_json=books_response.json()
                    books_list=response_json['stories']
                    for book in books_list:
                        book_id=book['id']
                        title=book['title']
                        book_url=book['url']
                        book_reads=book['readCount']
                        totalVotes=book['voteCount']
                        num_parts=book['numParts']
                        time=book['length']/69000
                        time=float("{:.2f}".format(time)) 
                        author=book['user']['name']
                        status="Ongoing"
                        if book['completed']==True:
                            status='Completed'
                        mature_status=book['mature']
                        description=book['description']
                        tags=book['tags']
                        chapter1_publish_date=book['firstPublishedPart']['createDate'][:10]
                        self.ans.loc[len(self.ans.index)] = [self.category,title,book_url,book_reads,totalVotes,num_parts,time,author,status,mature_status,description,tags,chapter1_publish_date,book_id]
            else:
                    print(f"Could not fetch books for genre: {self.category}...")
                    print(f"Status code:{books_response.status_code}") 

    def closed(self,reason):
        self.ans.to_csv(f'{self.file_name}.csv',index=False)