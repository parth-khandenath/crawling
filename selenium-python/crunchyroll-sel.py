import pandas as pd
import undetected_chromedriver as uc
from bs4 import BeautifulSoup 
import time
from selenium.webdriver.common.by import By
import re

def process(num):
    try:
        num=str(num)
        if num[-1]=='k':
            return int(float(num[:-1])*1000)
        elif num[-1]=='m':
            return int(float(num[:-1])*1000000)
        return int(num)
    except Exception as e:
        print(e)
        return "NA"
    
def extract(s):
    pattern = r"S(\d+)\sE(\d+)"
    match = re.search(pattern, s)
    if match:
        episode_number = match.group(2)  # Extract the second group which represents the episode number
        print(s,match,episode_number)
        return episode_number
    return "NA"

driver=uc.Chrome()
driver.get('https://www.crunchyroll.com/videos/sci-fi/popular')   #change here
# driver.get('https://www.crunchyroll.com/videos/fantasy/popular')   #change here
filename="crunchyroll-sci-fi.csv"
time.sleep(7)

df_header={"bookId":[], "title":[], "bookUrl":[], "rating":[], "numOfRatings":[], "4+5 star reviews(%)":[], "numOfReviews":[], "episodesTotal":[], "introduction":[],  "tags":[], "publisher":[], "audio for education":[]}
try:
    df=pd.read_csv(filename)
except:
    df=pd.DataFrame(df_header)

st=4   #change here
# st=20   #change here
while(st>0):
    driver.execute_script("window.scrollTo(0, window.scrollY+6000)")
    time.sleep(3)
    st-=1

time.sleep(2)

soup=BeautifulSoup(driver.page_source,'lxml')
bleles=soup.select('.browse-card-hover__link--0BAl-')
baseurl='https://www.crunchyroll.com'
booklinks=[(baseurl+ele['href']) for ele in bleles]

print(len(booklinks))
canskip=True
c=0
for bl in booklinks:
    c+=1
    print(c,bl)
    # if bl=="https://www.crunchyroll.com/series/G79H2307W/mobile-suit-gundam-the-witch-from-mercury":    #for skipping
    #     canskip=False
    # if canskip:
    #     continue
    driver.get(bl)
    time.sleep(3)
    # try:
    #     driver.find_element(By.CSS_SELECTOR,'.show-more-episodes-btn').click()   #show more episodes button
    # except:
    #     pass
    time.sleep(3)
    soup2=BeautifulSoup(driver.page_source,'lxml')
    bookUrl='/'.join(bl.split('/')[:-1])
    bookId=bookUrl.split('/')[-1]
    title='NA'
    try:
        title=soup2.select_one('.hero-heading-line h1').text
    except:
        time.sleep(3)
        soup2=BeautifulSoup(driver.page_source,'lxml')
        try:
            title=soup2.select_one('.hero-heading-line h1').text
        except:
            title=soup2.select_one('.show-heading-line h1').text
    ratingdata=soup2.select_one('.star-rating-average-data__label--TdvQs').text
    rating=ratingdata.split()[0]
    numOfRatings=ratingdata.split()[1]
    numOfRatings=process(numOfRatings[1:-1])
    reviews=(soup2.select_one('.star-rating__reviews-link--lkG9- .text--is-m--pqiL-').text[:-8]).replace(',','')
    driver.find_element(By.CSS_SELECTOR,'.call-to-action--PEidl.call-to-action--is-s--xFu35.expandable-section__button--KeiDD').click()  #expanding intro
    # time.sleep(0.4)
    atts=12
    while True:
        try:
            driver.find_element(By.CSS_SELECTOR,'.star-rating-short__trigger-icon---MKmu').click()   #expanding % wise ratings
            time.sleep(0.5)
            pr_eles=driver.find_elements(By.CSS_SELECTOR,'.rating-data-toggletip-scale--Hpj83.rating-data-toggletip__scale--HMhze p.text--gq6o-.text--is-l--iccTo.rating-data-toggletip-scale__rating-value--YVO0Z')
            prs=[(ele.text).replace("%","") for ele in pr_eles]
            pr4n5=int(prs[0])+int(prs[1])
            break
        except:
            pr4n5="NA"
            atts-=1
            if atts==0:
                break
            driver.execute_script("window.scrollTo(0, window.scrollY+9000)")
            time.sleep(1)
    
    # totalepis=len(driver.find_elements(By.CSS_SELECTOR,'.card'))
    lastepisode=soup2.select_one("a.playable-card__title-link--96psl").text
    totalepis=extract(lastepisode)
    try:
        intro=driver.find_element(By.CSS_SELECTOR,'.expandable-section--is-expanded--8vmUz .expandable-section__text---00oG').text
    except:
        intro="NA"
    teles=driver.find_elements(By.CSS_SELECTOR,'.badge__text-wrapper--is-link--7wvjx')
    tags=[ele.text for ele in teles]
    tags='-'.join(tags)
    info=driver.find_elements(By.CSS_SELECTOR,'.details-table__table-column-value--KeNXo')
    publisher=info[0].text
    try:
        audio=info[1].text
    except Exception as e:
        print(e)
        audio="NA"

    df.loc[len(df.index)]=['crunchyroll-'+bookId,title,bookUrl, rating,numOfRatings,pr4n5,reviews,totalepis,intro,tags,publisher,audio]
    df.to_csv(filename,index=False)

driver.close()