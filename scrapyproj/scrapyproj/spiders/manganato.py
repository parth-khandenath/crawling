import scrapy
import docx
import time
import pandas as pd
from bs4 import BeautifulSoup as bs

class manganato(scrapy.Spider):
    name = 'manganato'
    def __init__(self, **kwargs):

        self.bookname = "The Alpha's Addiction"  #change here
        self.start_urls = [ 
            "https://chapmanganato.to/manga-dr980474",
            "https://chapmanganato.to/manga-bn978870",
            "https://chapmanganato.to/manga-bt978676",
            "https://chapmanganato.to/manga-ax951880",
            "https://chapmanganato.to/manga-bf979214",
            "https://chapmanganato.to/manga-ci980191",
            "https://chapmanganato.to/manga-dg980989",
            "https://chapmanganato.to/manga-wj973392",
            "https://chapmanganato.to/manga-aa951409",
            "https://chapmanganato.to/manga-to970571",
            "https://chapmanganato.to/manga-va953509",
            "https://chapmanganato.to/manga-tz953334",
            "https://chapmanganato.to/manga-gr983826",
            "https://chapmanganato.to/manga-fr982926",
            "https://chapmanganato.to/manga-wd951838",
            "https://chapmanganato.to/manga-qm951521",
            "https://chapmanganato.to/manga-ah978064",
            "https://chapmanganato.to/manga-dk980967",
            "https://chapmanganato.to/manga-ec981811",
            "https://chapmanganato.to/manga-gt984176",
            "https://chapmanganato.to/manga-zd976838",
            "https://chapmanganato.to/manga-aa951883",
            "https://chapmanganato.to/manga-jq951973",
            "https://chapmanganato.to/manga-qi951517",
            "https://chapmanganato.to/manga-hu985229",
            "https://chapmanganato.to/manga-ej981992",
            "https://chapmanganato.to/manga-do980949",
            "https://chapmanganato.to/manga-eu982203",
            "https://chapmanganato.to/manga-cw979879",
            "https://chapmanganato.to/manga-yg951863",
            "https://chapmanganato.to/manga-ef951662",
            "https://chapmanganato.to/manga-ac977685",
            "https://chapmanganato.to/manga-zd976712",
            "https://chapmanganato.to/manga-cu979729",
            "https://chapmanganato.to/manga-bu979277",
            "https://chapmanganato.to/manga-jz987182",
            "https://chapmanganato.to/manga-ai977917",
            "https://chapmanganato.to/manga-vv973156",
            "https://chapmanganato.to/manga-ba979135",
            "https://chapmanganato.to/manga-gv952204",
            "https://chapmanganato.to/manga-eh951664",
            "https://chapmanganato.to/manga-ie985687",
            "https://chapmanganato.to/manga-nc952011",
            "https://chapmanganato.to/manga-ax977806",
            "https://chapmanganato.to/manga-ko987549",
            "https://chapmanganato.to/manga-je987087",
            "https://chapmanganato.to/manga-ag977815",
            "https://chapmanganato.to/manga-ik985693",
            "https://chapmanganato.to/manga-wl951846",
            "https://chapmanganato.to/manga-gi983617",
         ]
        self.df_header = {'title':[], 'chapter':[], 'views':[], 'date':[]}
        self.output_dict={}
                
    custom_settings={
        'CONCURRENT_REQUESTS':100,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'
    }
    
    def parse(self,response):
        title=response.css('h1::text').get()
        chap_names=response.css('.chapter-name::text').getall()
        chap_views=response.css('.chapter-view::text').getall()
        chap_times=response.css('.chapter-time::text').getall()
        df=pd.DataFrame(self.df_header)
        for i in range(len(chap_names)):
            if ':' in chap_names[i]:
                chap_names[i] = chap_names[i].split(':')[0]
            df.loc[len(df.index)]=[title, chap_names[i], self.processNum(chap_views[i]), chap_times[i]]
        self.output_dict[title]=df
        
    def processNum(self, num):
        num=str(num)
        if num[-1]=='K':
            num=int(float(num[:-1])*1000)
        elif num[-1]=='M':
            num=int(float(num[:-1])*1000000)
        return int(num)

    def closed(self,reason):
        for name, df in self.output_dict.items():
            name=name.replace(',','').replace('?','')
            df.to_csv(f'./out/{name}.csv',index=False)