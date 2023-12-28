import undetected_chromedriver as uc
import pandas as pd
import time
from selenium.webdriver.common.by import By

head = {
    "Title" :[],
    "URL":[],
    "Chapters":[],
    "Frequency":[],
    "Readers":[],
    "Reviews":[],
    "Last Update":[],
    # "Tags":[],
    "Language":[],
    "Publisher name":[]
}

options = uc.ChromeOptions() 
options.page_load_strategy = 'eager'
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

driver = uc.Chrome(options=options)

site='https://www.novelupdates.com/list-original-publisher/?st=1&sort=count&order=desc&pg='
start=2
end=3

ans=pd.DataFrame(head)

for pg_no in range(start,end+1): #iterating over each page of novelupdates
    driver.get(site+str(pg_no))
    time.sleep(2)
    publishers=driver.find_elements(By.CSS_SELECTOR,'.wpb_wrapper li a') #get all publishrs of this page
    pub_links=[]
    pub_names=[]
    for pub in publishers:
        pub_links.append(pub.get_attribute('href'))
        pub_names.append(pub.get_attribute('innerHTML'))
    starttt=0
    if pg_no==2:
        starttt=31
    for j in range(starttt,len(pub_links)): #going inside publishers
        driver.get(pub_links[j]) 
        time.sleep(1)
        page_btns=driver.find_elements(By.CSS_SELECTOR,'.digg_pagination a:not(.next_page)')
        if len(page_btns)>0:
            last_page= (page_btns[-1]).get_attribute('innerHTML')
            last_page= int(last_page)
        else:
            last_page=1
        for pub_page in range(1,last_page+1):  #moving over each page of a publisher
            driver.get(pub_links[j]+f'?st=1&pg={pub_page}') 
            #fetching details of books of this page of publisher
            book_ttls_urls=driver.find_elements(By.CSS_SELECTOR,f'.search_title a')
            book_chapts=driver.find_elements(By.CSS_SELECTOR,f'.ss_desk:nth-child(1)')
            book_freqs=driver.find_elements(By.CSS_SELECTOR,f'.ss_desk:nth-child(2)')
            book_reads=driver.find_elements(By.CSS_SELECTOR,f'.ss_desk:nth-child(3)')
            book_reviews=driver.find_elements(By.CSS_SELECTOR,f'.ss_desk:nth-child(4)')
            book_luds=driver.find_elements(By.CSS_SELECTOR,f'.ss_desk:nth-child(5)')
            book_no=1
            while book_no<=25:  
                try:
                    title=book_ttls_urls[book_no].get_attribute('innerHTML')
                    url=book_ttls_urls[book_no].get_attribute('href')
                    chapts=book_chapts[book_no].get_attribute('innerHTML')
                    chapts=chapts.split('</i>')[1]
                    freq=book_freqs[book_no].get_attribute('innerHTML')
                    freq=freq.split('</i>')[1]
                    readers=book_reads[book_no].get_attribute('innerHTML')
                    readers=readers.split('</i>')[1]
                    reviews=book_reviews[book_no].get_attribute('innerHTML')
                    reviews=reviews.split('</i>')[1]
                    last_update=book_luds[book_no].get_attribute('innerHTML')
                    last_update=last_update.split('</i>')[1]
                    # tags=[]
                    # for tag in driver.find_elements(By.CSS_SELECTOR,f'.search_genre:nth-child({book_no}) a.gennew.search'):
                    #     tags.append(tag.get_attribute('innerHTML'))
                    language=driver.find_element(By.CSS_SELECTOR,f'.search_ratings span').get_attribute('innerHTML')
                    publisher_name=pub_names[j]
                    ans.loc[len(ans.index)]=[title,url,chapts,freq,readers,reviews,last_update,#tags,
                    language,publisher_name]
                    book_no+=1
                except Exception as e: #last page may have less than 25 books
                    print(e)
                    print(book_no)
                    print(pub_names[j])
                    break   
            ans.to_csv('novel_updates5.csv') #saving after each publisher
        
        
