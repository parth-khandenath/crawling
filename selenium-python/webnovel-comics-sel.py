import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup 
import time
import re

def extract_hashtags(text):
    try:
        hashtags = re.findall(r'#\w+', text)
        return hashtags
    except:
        return []
    
def process(num):
    num=str(num)
    if num[-1]=='M':
        num=int(float(num[:-1])*1000000)
    elif num[-1]=='K':
        num=int(float(num[:-1])*1000)
    return str(num)

links=['https://www.webnovel.com/stories/comic-fantasy?bookStatus=0&orderBy=1','https://www.webnovel.com/stories/comic-fantasy?bookStatus=0&orderBy=2','https://www.webnovel.com/stories/comic-fantasy?bookStatus=0&orderBy=3','https://www.webnovel.com/stories/comic-magic?bookStatus=0&orderBy=1','https://www.webnovel.com/stories/comic-magic?bookStatus=0&orderBy=2','https://www.webnovel.com/stories/comic-magic?bookStatus=0&orderBy=3','https://www.webnovel.com/stories/comic-sports?bookStatus=0&orderBy=1','https://www.webnovel.com/stories/comic-sports?bookStatus=0&orderBy=2','https://www.webnovel.com/stories/comic-sports?bookStatus=0&orderBy=3','https://www.webnovel.com/stories/comic-inspiring?bookStatus=0&orderBy=1','https://www.webnovel.com/stories/comic-inspiring?bookStatus=0&orderBy=2','https://www.webnovel.com/stories/comic-inspiring?bookStatus=0&orderBy=3','https://www.webnovel.com/stories/comic-drama?bookStatus=0&orderBy=1','https://www.webnovel.com/stories/comic-drama?bookStatus=0&orderBy=2','https://www.webnovel.com/stories/comic-drama?bookStatus=0&orderBy=3','https://www.webnovel.com/stories/comic-wuxia?bookStatus=0&orderBy=1','https://www.webnovel.com/stories/comic-wuxia?bookStatus=0&orderBy=2','https://www.webnovel.com/stories/comic-wuxia?bookStatus=0&orderBy=3','https://www.webnovel.com/stories/comic-slice-of-life?bookStatus=0&orderBy=1','https://www.webnovel.com/stories/comic-slice-of-life?bookStatus=0&orderBy=2','https://www.webnovel.com/stories/comic-slice-of-life?bookStatus=0&orderBy=3','https://www.webnovel.com/stories/comic-cooking?bookStatus=0&orderBy=1','https://www.webnovel.com/stories/comic-cooking?bookStatus=0&orderBy=2','https://www.webnovel.com/stories/comic-cooking?bookStatus=0&orderBy=3']

driver=uc.Chrome()
df_header = { 'bookName':[], 'url':[], 'genre':[], 'status':[],'lastChapterTime':[],'publisher':[], 'views':[], 'chapterCount':[], 'firstChapterDate':[], 'description':[], 'tags':[], 'rating':[], 'numOfRatings':[], 'drawingQuality':[], 'storyDevelopment':[], 'characterDesign':[]}
for link in links:
    print('link: ',link)
    genre=(link.split('?')[0]).split('comic-')[-1]
    if genre=="slice-of-life":
        genre="Slice-of-Life"
    else:
        genre=genre[0].upper() + genre[1:]
    order=link.split('=')[-1]
    if order=='1':
        order='most-popular'
    elif order=='2':
        order='recommended'
    elif order=='3':
        order='most-collections'
    try:
        df=pd.read_csv(f'webnovel-comics-{genre}-{order}.csv')
    except:
        df=pd.DataFrame(df_header)
    driver.get(link)
    time.sleep(3)
    soup=BeautifulSoup(driver.page_source,'lxml')
    bookeles=soup.select('li div.pr')
    for ele in bookeles:
        booklink='https://www.webnovel.com/comic/'+(ele.select_one('h3 a.c_l')['href']).split('_')[-1]
        print('booklink: ',booklink)
        driver.get(booklink)
        time.sleep(3)
        soup2=BeautifulSoup(driver.page_source,'lxml')
        title=soup2.select_one('div h1').text
        status='Not available'
        chapters='NA'
        views='NA'
        stats=soup2.select('strong span')  
        for stat in stats:
            if 'Completed' in stat.text:
                status='Completed'
            elif 'Chapters' in stat.text:
                chapters=stat.text[:-9]
            elif 'Views' in stat.text:
                views=stat.text[:-6]
                views=process(views)
        publisher=soup2.select_one('h2.mb12.fw400').text
        publisher=publisher[12:]
        summary=soup2.select_one('.j_synopsis p.c_000').text
        tags=extract_hashtags(summary)
        tags='-'.join(tags)
        if tags=='':
            tags='NA'
        try:
            reviews=soup2.select_one('.j_total_book_review').text
            rating=soup2.select_one('small.fl').text
            rating_stats=soup2.select('ul.rev-score-list .g_star')
            dq=rating_stats[0].select('._on')
            if dq:
                dq=len(dq)
            else:
                dq=0
            sd=rating_stats[1].select('._on')
            if sd:
                sd=len(sd)
            else:
                sd=0
            cd=rating_stats[2].select('._on')
            if cd:
                cd=len(cd)
            else:
                cd=0
        except:
            reviews='NA'
            rating='NA'
            dq='NA'
            sd='NA'
            cd='NA'
        ur = booklink+'/catalog'
        driver.get(ur)
        time.sleep(3)
        soup3 = BeautifulSoup(driver.page_source,"lxml")
        latest_chapter_time = soup3.select_one('.c_s.ml8').text
        first_chapter_time = soup3.select_one('small.c_s.fs12.lh16').text    
        df.loc[len(df.index)] = [title,booklink,genre,status,latest_chapter_time,publisher,views,chapters,first_chapter_time,summary,tags,rating,reviews,dq,sd,cd]
        df.to_csv(f'webnovel-comics-{genre}-{order}.csv',index=False)
