import scrapy
import pandas as pd
import json

class QuoteSpider(scrapy.Spider):
    name = 'wattpad_genre'
    start_urls = [
        'https://api.wattpad.com/']
    custom_settings={
        'CONCURRENT_REQUESTS':10,
        'DOWNLOAD_DELAY': 1,  # Add delay between requests
        'headers' : {
        'authority': 'api.wattpad.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': 'wp_id=ca8ae818-ec45-46f8-988f-8b7f0b744243; lang=1; locale=en_US; _col_uuid=b44b2218-c32d-47f0-8126-02961550cf8e-hv9s; _fbp=fb.1.1702271570875.1212863649; _pubcid=cd9caa39-f24b-4a61-baca-079795eaf5a1; fs__exp=5; wp-web-page=true; token=455583260%3A2%3A1702362428%3Ay7QdX5G4ZhXK9ZfmYncm_-bbylNQk7aJNlkGf431KXykFM4XJy10xFwLbMOliyEO; te_session_id=1703153995517; _gid=GA1.2.978387512.1703153997; AMP_TOKEN=%24NOT_FOUND; _ga=GA1.2.1488413246.1702271567; cto_bundle=PEUblV9GN2Q2SCUyQkIlMkZzYnVmajM3N2Y5MFlIemdUbVFSZjdnSVlzM3IyJTJGc2Z0ZHh0Y3N0WklvUXNidExCOUJkbEN1MnNVSCUyQjBNbTVvJTJGbCUyQjlsVHFWZlFHN3RFUDkxWXBBRDVsZkZHZyUyQnNKRzY3VkdGNnoyOU5PWGtvUWgwUkZwV0lyR2ZnYkx2SmgyeVViM1FBUGptdUo3R1ZIMXA2dnVkQ2NUUEdpQWg1ZzU4eEJSYldGUXBYJTJCclJrcFNMQ2RUSjR6eiUyRmtldXVvSEpvNzR1bGdwUkVIWGhhakJRJTNEJTNE; _ga_FNDTZ0MZDQ=GS1.1.1703160945.10.1.1703162525.0.0.0; lang=1; locale=en_US',
        'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
    }
    file_name=""
    sheet = 'wattpad_listing'
    Headers = {"title":[] ,"book id":[], "book_url":[], "read_count":[] , "vote_count":[], "parts":[], "time (hrs.)":[], "author":[], "status":[], "mature_status":[], "description":[], "tags":[], "chapter1_publish_date":[]}
    ans = pd.DataFrame(Headers)
    cup=1000000000

    def parse(self,response):
        limit=100 #change here    #max limit (api se pata chala)
        offset=0
        A=['athlete']#change here  
        for genre in A:
            self.file_name=f'wattpad_{genre}_listing'
            while offset<1200:#change here           # total no of stories (api se pata chala)
                url=f"https://api.wattpad.com/v5/hotlist?tags={genre}&language=1&offset={offset}&limit={limit}"
                self.cup-=10000
                yield response.follow( url=url, callback=self.page, priority=self.cup, meta={'p':self.cup,'genre':genre})
                offset+=limit
            offset=0
    

    def page(self,response):
        res=response.json()
        data=response.meta
        p=data['p']
        genre=data['genre']
        stories=res['stories']
        count=0
        for story in stories:
            count+=1
            book_id=story["id"]

            mature_status=story['mature']
        
            # #url=f"https://www.wattpad.com/api/v3/stories/{book_id}?wordCount"
            url=f"https://www.wattpad.com/api/v3/stories/{book_id}?fields=id%2Ctitle%2CcreateDate%2CmodifyDate%2CvoteCount%2CreadCount%2CcommentCount%2Cdescription%2Curl%2CfirstPublishedPart%2Ccover%2Clanguage%2CisAdExempt%2Cuser(name%2Cusername%2Cavatar%2Clocation%2Chighlight_colour%2CbackgroundUrl%2CnumLists%2CnumStoriesPublished%2CnumFollowing%2CnumFollowers%2Ctwitter)%2Ccompleted%2CisPaywalled%2CpaidModel%2CnumParts%2ClastPublishedPart%2Cparts(id%2Ctitle%2Clength%2Curl%2Cdeleted%2Cdraft%2CcreateDate%2CscheduledPublishDatetime%2CwordCount%2CreadCount%2CvoteCount)%2Ctags%2Ccategories%2Crating%2Crankings%2CtagRankings%2Clanguage%2CstoryLanguage%2Ccopyright%2CsourceLink%2CfirstPartId%2Cdeleted%2Cdraft%2ChasBannedCover%2Clength"
            yield response.follow( url=url, callback=self.book, priority=p - 100, meta={'p':p - 100,'book_id':book_id,'genre':genre,'mature':mature_status} )

    def book(self,response):   # landing on Book's home page
        res=response.json()
        totalReads=res["readCount"]
        # if totalReads<100000: #not listing books with <100K reads
        #     return
        data=response.meta
        mature_status=data["mature"]
        book_url=res["url"]
        book_name=res["title"]
        totalVotes=res["voteCount"]
        num_parts=res["numParts"]
        time=res['length']/70000
        time=float("{:.2f}".format(time))
        author=res['user']['username']
        status="Ongoing"
        if res['completed']==True:
            status="Completed"
        description=res['description']
        tags=str([tag for tag in res["tags"]])
        chapter1_publish_date=res['firstPublishedPart']['createDate'][:10]

        self.ans.loc[len(self.ans.index)] = [book_name,data['book_id'],book_url,totalReads,totalVotes,num_parts,time,author,status,mature_status,description,tags,chapter1_publish_date]
        self.ans.to_csv(f'{self.file_name}.csv',index=False)

    # def closed(self,reason):
    #     self.ans.to_csv(f'{self.file_name}.csv',index=False)

# adventure - 1200
# horror - 1200
# mystery - 1200
# paranormal - 1200
# sciencefiction - 1200
# thriller - 1200
# contemporarylit - 662
# fantasy - 1200
# humor - 1200
# newadult - 1200
# werewolf - 1200
# diverselit - 1200
# historicalfiction - 1200
# teenfiction - 1200
# romance - 1200
# nonfiction - 1200
# lgbt - 1200

# sportsromance - 447 - want all books here
# sports - 1200 - want all books here
# athlete - 1200 - want all books here