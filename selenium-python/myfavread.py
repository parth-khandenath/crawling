import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup as bs
import pandas as pd
import time

def processNum(num):
    try:
        num=str(num)
        if num[-1]=='K':
            return int(float(num[:-1])*1000)
        elif num[-1]=='M':
            return int(float(num[:-1])*1000000)
        return int(num)
    except Exception as e:
        print(e)
        return "NA"

df_headers={'id':[],'title':[],'url':[],'genre':[],'author':[],'star_rating':[],'reviews':[],'fans':[],'chapters':[],'views':[],'status':[],'age_rating':[],'updated':[],'tags':[],'synopsis':[]}
try:
    df=pd.read_csv('myfavread.csv')
except:
    df=pd.DataFrame(df_headers)

links = [   #links of pages with catalogs of books
    'https://www.myfavreads.com/novels',
    'https://www.myfavreads.com/events/romance-contest-2023/'
]
opts=uc.ChromeOptions()
opts.page_load_strategy = 'eager'
driver=uc.Chrome(options=opts)

booklinks=[
        'https://www.myfavreads.com/novel/069400106933810749559',     #harcoded carousel books   #change 
        'https://www.myfavreads.com/novel/461576668005870766073',
        'https://www.myfavreads.com/novel/165121334220856399411',
        'https://www.myfavreads.com/novel/857899640931695039184',
        'https://www.myfavreads.com/novel/937836607002148108368',
        'https://www.myfavreads.com/novel/340994715602825291047',
        'https://www.myfavreads.com/novel/273476338960230700391',
        'https://www.myfavreads.com/novel/261106443123760889433'
    ]

authors_page='https://www.myfavreads.com/authors'
author_links=['https://www.myfavreads.com/author/bpvD3b45koDFkCeVettK9o']       #weekly featured author hardcoded  #change 
driver.get(authors_page)
time.sleep(5)
auth_eles=driver.find_elements(By.XPATH,"//a[.//div[contains(@class, 'q-avatar')]]")
for auth in auth_eles:
    author_links.append(auth.get_attribute('href'))
for auth_link in author_links:
    driver.get(auth_link)
    time.sleep(8)
    beles=driver.find_elements(By.CSS_SELECTOR,'.q-tab-panel .q-pl-md a')
    for bele in beles:
        booklinks.append(bele.get_attribute('href'))

for link in links:
    driver.get(link)
    time.sleep(5)
    book_a_tags=driver.find_elements(By.CSS_SELECTOR,'.column.q-py-md a')
    
    for a_tag in book_a_tags:
        booklinks.append(a_tag.get_attribute('href'))
    
for bl in booklinks: #open and scrape books
    driver.get(bl)
    print(bl)
    time.sleep(5)
    id='favread-'+bl.split('/')[-1]
    title=driver.find_element(By.CSS_SELECTOR,'.novel-title').text
    info=driver.find_element(By.CSS_SELECTOR,'.novel-author').text
    genre=(info.split('By')[0]).strip()
    author=(info.split('By')[1]).strip()
    row_eles=driver.find_elements(By.CSS_SELECTOR,'.col.column.q-ml-sm .row')
    star_rating=row_eles[0].find_elements(By.CSS_SELECTOR,'span.q-ml-sm')[0].text
    reviews=row_eles[0].find_elements(By.CSS_SELECTOR,'span.q-ml-sm')[1].text
    fans=row_eles[2].find_element(By.CSS_SELECTOR,'.dark-sub-heading-font').text
    fans=processNum(fans)
    chapters=row_eles[3].find_element(By.CSS_SELECTOR,'.dark-sub-heading-font').text
    views=row_eles[4].find_element(By.CSS_SELECTOR,'.dark-sub-heading-font').text
    views=processNum(views)
    status=row_eles[5].find_element(By.CSS_SELECTOR,'.dark-sub-heading-font').text
    age_rating=row_eles[6].find_element(By.CSS_SELECTOR,'.dark-sub-heading-font').text
    updated='NA'
    tags=[]
    for i in range(len(row_eles)):
        if i>6:
            if 'Updated' in row_eles[i].text:
                updated=row_eles[i].find_element(By.CSS_SELECTOR,'.dark-sub-heading-font').text
            if 'Tags' in row_eles[i].text:
                for eleee in row_eles[i].find_elements(By.CSS_SELECTOR,'.dark-sub-heading-font'):
                    tags.append(eleee.text)
    tags='-'.join(tags)
    try:
        more_button=driver.find_element(By.CSS_SELECTOR,'.vue-truncate-html__button.vue-truncate-html__button_more')
        more_button.click()
    except:
        pass
    synopsis=driver.find_element(By.CSS_SELECTOR,'.vue-truncate-html').text

    df.loc[len(df.index)]=[id,title,bl,genre,author,star_rating,reviews,fans,chapters,views,status,age_rating,updated,tags,synopsis]
    df.to_csv('myfavread.csv',index=False)

driver.quit()