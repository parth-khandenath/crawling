import scrapy
import re
import pandas as pd


class novelUpdates(scrapy.Spider):
    name = "novel_updates"
    allowed_domains = ["www.novelupdates.com"]
    # data_url = "https://www.dreame.com/all-genres/8-ya-teenfiction.html?page={}"
    filename='novelupdates-horror'
    start_urls = ['https://www.novelupdates.com/genre/horror/?sort=4&order=2&status=1&pg=1']
    p = 100000000
    df_headers = {
        "Title": [],
        "numOfChps": [],
        "status": [],
        "lastepisode": [],  
        "Tags": [],
        "url": [],
        "description": [], #
        "type": [],
        "genre": [],
        "tags2": [],
        "ratings split": [],
        "rating":[],
        "votes": [],
        "language": [],
        "author": [],
        "artist": [],
        "year": [],
        "original publiser": [],
        "english publisher": [],
        "release frequency": [],
        "readers": [],
        "reading list rank": [],
        "reviews": [],
        'activity status rank':[]
    }
    try: 
        ans=pd.read_csv(f'{filename}.csv')
    except:
        ans = pd.DataFrame(df_headers)
            
    def parse(self,response):
        for i in range(1,30):
            self.p-=10000
            url=f"https://www.novelupdates.com/genre/horror/?sort=4&order=2&status=1&pg={i}" 
            yield response.follow(url=url, callback=self.parse_page,priority=self.p,meta={'p':self.p})

    def parse_page(self, response):
        p=response.meta['p']
        titles=response.css('.search_title a::text')
        urls=response.css('.search_title a::href')
        chaps=response.css('.ss_desk:nth-child(1)::text')
        freqs=response.css('.ss_desk:nth-child(2)::text')
        readerss=response.css(".ss_desk:nth-child(3)::text").get()
        revss=response.css(".ss_desk:nth-child(4)::text").get()
        statuss=['NA']*25
        lastepis=response.css('.ss_desk:nth-child(5)::text')
        tagss=[]
        for i,ele in enumerate(response.css('.search_genre')):
            tgs=[]
            for t in ele:
                if 'Completed' in t.css("::text").get():
                    statuss[i]='Completed'
                else:
                    tgs.append(t.css("::text").get())
            tagss.append('-'.join(tgs))
        for i in range(len(urls)):
            p-=100
            meta={'title':titles[i],'url':urls[i],'chaps':chaps[i],'status':statuss[i],'lastepi':lastepis[i],'tags':tagss[i],'freq':freqs[i],'readers':readerss[i],'reviews':revss[i]}
            yield response.follow(url=urls[i],callback=self.parse_book,meta=meta,priority=p)

    def parse_book(self, response):
        meta=response.meta
        
        title=meta['title']
        url=meta['url']
        chaps=meta['chaps']
        status=meta['status']
        lastepi=meta['lastepi']
        tags=meta['tags']
        freq=meta['freq']
        reads=meta['freq']
        revs=meta['freq']

        desc=response.css('#editdescription p::text')
        type=response.css('#showtype::text')
        genre='-'.join(response.css('#seriesgenre .genre::text'))
        tags2='-'.join(response.css('#etagme::text'))
        rating_split=''
        for r in response.css('table#myrates tr'):
            rating_split+=f'{r.css(' .rating::text')}:{r.css(' .votetext::text')}'
        votes=response.css("#taghidemsg+ .seriesother .uvotes::text").replace('(','').replace(')','').split(',')[1]
        rating=response.css("#taghidemsg+ .seriesother .uvotes::text").replace('(','').replace(')','').split(',')[0].split('/')[0]
        lang=response.css('#showlang::text')
        author=response.css('#showauthors::text').get()
        artist=response.css('#showartists::text').get()
        year=response.css("#edityear::text").get()
        orig_pub=response.css("#showopublisher::text").get()
        eng_pub=response.css("#myepub::text").get()
        rlrank=''
        acsr=''

        weekly_rank = response.xpath('//h5[@class="seriesother"]/following-sibling::text()[contains(., "Weekly Rank")]/following-sibling::span[@class="userrate rank"]/text()').get()
        # Extract Monthly Rank
        monthly_rank = response.xpath('//h5[@class="seriesother"]/following-sibling::text()[contains(., "Monthly Rank")]/following-sibling::span[@class="userrate rank"]/text()').get()
        # Extract All Time Rank
        all_time_rank = response.xpath('//h5[@class="seriesother"]/following-sibling::text()[contains(., "All Time Rank")]/following-sibling::span[@class="userrate rank"]/text()').get()
        acsr+='weekly:'+weekly_rank
        acsr+='monthly:'+monthly_rank
        acsr+='all time:'+all_time_rank
        # Extract Reading Lists Monthly Rank
        reading_lists_monthly_rank = response.xpath('//b[@class="rlist"]/following-sibling::text()[contains(., "Monthly Rank")]/following-sibling::span[@class="userrate rank"]/text()').get()
        # Extract Reading Lists All Time Rank
        reading_lists_all_time_rank = response.xpath('//b[@class="rlist"]/following-sibling::text()[contains(., "All Time Rank")]/following-sibling::span[@class="userrate rank"]/text()').get()
        rlrank+='monthly:'+reading_lists_monthly_rank
        rlrank+='all time:'+reading_lists_all_time_rank

        self.ans.loc[len(self.ans.index)] = [
            title,chaps,status,lastepi,tags,url,desc,type,genre,tags2,rating_split,rating,votes,lang,author,artist,year,orig_pub,eng_pub,freq,reads,rlrank,revs,acsr
        ]

        self.ans.to_csv(f"{self.filename}.csv", index=False)