import scrapy
import pandas as pd
import json
import time

class QuoteSpider(scrapy.Spider):
    name = 'wattpad_author'
    start_urls = [
        'https://api.wattpad.com/']
    custom_settings={
        'CONCURRENT_REQUESTS':1
    }
    file_name='wattpad_author'
    sheet = 'wattpad_listing'
    Headers = {"authorName":[],"userName":[],"votesReceived":[],"numStoriesPublished":[],"numFollowers":[],
               "location":[],"facebook":[],"twitter":[],"website":[],"author Bio":[],"book_name_hit":[],
               "book_id_hit":[],"languageName":[],"rating_hit":[],"totalReads_hit_book":[],"totalVotes_hit_book":[],
                "tags_hit_book":[], "genre_hit_book":[], "genreRank_hit_book":[], "firstPublishedPart":[],
                "lastPublishedPart":[], "chaptersTotal_hit_book":[], "timeReadApprox(hours)_hit_book":[], "hit_book_url":[]}
    # file_name='wattpad_author'
    ans = pd.DataFrame(Headers)
    cup=1000000000
    hours_content_limit=5    #hours, requirement from novels content team

    def parse(self,response):
        limit=200
        offset=0
        A=['fantasy']  #,'horror', 'thriller', 'romance'  ,'sciencefiction','fantasy']    #requested categories, current implementation is 1 by 1 in array, can update by keeping 5 different ans pandas list
        for genre in A:
            self.file_name=f'wattpad_{genre}_{self.hours_content_limit}hr_content'
            while offset<1000:      # hardcoded for no of books to search for
                url=f"https://api.wattpad.com/v5/hotlist?tags={genre}&language=1&offset={offset}&limit={limit}"
                self.cup-=1000000
                yield response.follow( url=url, callback=self.page_parse, priority=self.cup, meta={'p':self.cup,'genre':genre})
                offset+=limit
            offset=0
    

    def page_parse(self,response):
        res=response.json()
        data=response.meta
        p=data['p']
        genre=data['genre']
        stories=res['stories']
        count=0
        for story in stories:
            book_id=story['id']
            count+=1
            #url=f"https://www.wattpad.com/api/v3/stories/{book_id}?wordCount"
            url=f"https://www.wattpad.com/api/v3/stories/{book_id}?fields=id%2Ctitle%2CcreateDate%2CmodifyDate%2CvoteCount%2CreadCount%2CcommentCount%2Cdescription%2Curl%2CfirstPublishedPart%2Ccover%2Clanguage%2CisAdExempt%2Cuser(name%2Cusername%2Cavatar%2Clocation%2Chighlight_colour%2CbackgroundUrl%2CnumLists%2CnumStoriesPublished%2CnumFollowing%2CnumFollowers%2Ctwitter)%2Ccompleted%2CisPaywalled%2CpaidModel%2CnumParts%2ClastPublishedPart%2Cparts(id%2Ctitle%2Clength%2Curl%2Cdeleted%2Cdraft%2CcreateDate%2CscheduledPublishDatetime%2CwordCount%2CreadCount%2CvoteCount)%2Ctags%2Ccategories%2Crating%2Crankings%2CtagRankings%2Clanguage%2CstoryLanguage%2Ccopyright%2CsourceLink%2CfirstPartId%2Cdeleted%2Cdraft%2ChasBannedCover%2Clength"
            yield response.follow( url=url, callback=self.book_parse, priority=p - count *100, meta={'p':p - count *100,'book_id':book_id,'genre':genre} )
            time.sleep(.01)
    def book_parse(self,response):   # landing on Book's home page
        res=response.json()
        data=response.meta
        p=data['p']
        genre=data['genre']
        book_id=data['book_id']
        length=res['length']
        if int(length)/70000>self.hours_content_limit:
            book_name =  res['title']  #name
            author = res['user']['username'] #author name
            languageName=res['language']['name']
            rating=res['rating']
            totalReads=res['readCount']
            totalVotes = res['voteCount']   #likes
            tags = res['tags']
            tags = str([tag for tag in tags])  #genre
            createDate=res['createDate']
            firstPublishedPart=res['firstPublishedPart']['createDate']
            lastPublishedPart=res['lastPublishedPart']['createDate']
            # isPaywalled=res['isPaywalled']
            chaptersTotal=res['numParts']
            timeReadApprox=int(length)/70000
            timeReadApprox=float("{:.2f}".format(timeReadApprox))
            parts=res['parts']
            book_url=res['url']
            tagRankings=res['tagRankings']
            rank=''
            for tagRanking in tagRankings:
                if tagRanking['name']==genre:
                    rank=tagRanking['rank']
              
            url=f"https://www.wattpad.com/api/v3/users/{author}?fields=username%2Cname%2Cdescription%2Cavatar%2CbackgroundUrl%2CcreateDate%2Clocation%2Cfollowing%2CfollowingRequest%2CnumFollowing%2Cfollower%2CfollowerRequest%2CnumFollowers%2CnumLists%2CnumStoriesPublished%2CvotesReceived%2Cfacebook%2Ctwitter%2Cwebsite%2Csmashwords%2Chighlight_colour%2Chtml_enabled%2Cverified%2Cambassador%2Cwattpad_squad%2Cis_staff%2Cprograms(wattpad_stars)%2CisPrivate%2CisMuted%2CexternalId%2Cnotes%2Csafety(isMuted%2CisBlocked)%2Cage%2Ccountry"
            yield response.follow( url=url, callback=self.author_parse, priority=p - 10, meta={'p':p - 10, "book_id":book_id,"book_name":book_name,"author":author, "languageName":languageName,"rating":rating,
             "totalReads":totalReads,"totalVotes":totalVotes,"tags":tags,"rank":rank,"firstPublishedPart":firstPublishedPart, 
             "lastPublishedPart":lastPublishedPart,"genre":genre, "chaptersTotal":chaptersTotal,"timeReadApprox":timeReadApprox, "book_url":book_url})


    def author_parse(self,response): 
        data=response.meta
        response=response.json()

        authorName=response['name']
        description=response['description']
        location=response['location']
        facebook=response['facebook']
        twitter=response['twitter']
        website=response['website']
        votesReceived=response['votesReceived']
        numStoriesPublished=response['numStoriesPublished']
        numFollowers=response['numFollowers']

        userName = data['author']
        book_id_hit = data['book_id']
        book_name_hit = data['book_name']
        languageName=data['languageName']
        rating_hit = data['rating']
        totalReads_hit_book = data['totalReads']
        totalVotes_hit_book = data['totalVotes']
        tags_hit_book = data['tags']
        genre_hit_book = data['genre']
        genreRank_hit_book = data['rank']
        firstPublishedPart = data['firstPublishedPart']
        lastPublishedPart = data['lastPublishedPart']
        chaptersTotal_hit_book = data['chaptersTotal']
        timeReadApprox_hit_book = data['timeReadApprox']
        hit_book_url = data['book_url']
        
        self.ans.loc[len(self.ans.index)] = [authorName, userName, votesReceived, numStoriesPublished, numFollowers, location, facebook, twitter, website, description, book_name_hit, book_id_hit, languageName, rating_hit, totalReads_hit_book, totalVotes_hit_book, tags_hit_book, genre_hit_book, genreRank_hit_book, firstPublishedPart, lastPublishedPart, chaptersTotal_hit_book, timeReadApprox_hit_book, hit_book_url]
        
        self.ans.to_csv(f'{self.file_name}.csv',index=False)