import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import pandas as pd
import time
from docx import Document
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import math
from selenium import webdriver

head = {
    "Title" :[],
    "URL":[],
    "book id":[],
    "Author":[],
    "Description":[],
    "Status":[],
    "Views":[],
    "Likes":[],
    # "Num of Chapters":[],
    "Tags":[],
    "Genre":[]
}
def get_text(soup,selector):
    return soup.select_one(selector).text
def wait_for_element_to_be_clickable(element):
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, element)))

options = uc.ChromeOptions() 
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

driver = uc.Chrome(options=options)

site='https://read.writekiss.com/'

driver.get(site)
time.sleep(4)
# driver.add_cookie={'_ga':'GA1.1.511260300.1702535612', '_ga_64XDRE5Q1B':'GS1.1.1702584222.3.1.1702584435.0.0.0'}
# driver.get(url)

c=9   #change this to index in categories list ( 0 based)
categories = ['Werewolf','Billionaire','After Hours','Contemporary','Sports Romance','New Adult','YA/Teen','Romantic Suspense','Sweet Romance']

driver.find_element(By.CSS_SELECTOR,'.kiss-h5-nav-menu-browse').click()
time.sleep(1)
if c==9:   #for paranormal genre #625 books
    driver.find_element(By.CSS_SELECTOR,".kiss-h5-nav-menu-pop-content-item.view-all").click()
    time.sleep(3)
    category = driver.find_elements(By.CSS_SELECTOR,".theme_item")[-1].click()
else:
    category = driver.find_element(By.CSS_SELECTOR,f"[title={categories[c]}]").click()

try:
    # ans = pd.read_csv(f'read_write_YA-Teen.csv') #/ causes directory issues
    ans = pd.read_csv(f"read_write_{categories[c]}.csv") 
except:
    ans = pd.DataFrame(head)

time.sleep(3)

i = len(ans)   #title no

print('starting from book: ', i)
lst = [0 for _ in range(0,1000)]
start=True
prev_book_skip=False

while i < 1000 :
    print("trying book no:",i)
    if lst[i] == 0:
        lst[i] = 1
        if prev_book_skip:
            prev_book_skip=False
            driver.execute_script("window.scrollTo(0, window.scrollY+200)")
        elif i >= 20:
            add=0
            if i%10 >= 3:
                add=1
            for j in range(0,((i)//10 )-1+add):
            # for j in range(0,((i)//10 )):
                time.sleep(1.2)
                driver.execute_script("window.scrollTo(0, window.scrollY+6000)")
                print(f'scroll big {j+1} times')
                time.sleep(0.8)#0.5 -> 0.8
            time.sleep(0.5)
    try:    
        element = f'.lazy_fresh_class:nth-child({i+1}) .book_title'
        status_element = f'.lazy_fresh_class:nth-child({i+1}) .book_status'
        view_element=f'.lazy_fresh_class:nth-child({i+1}) .static_title'
        # wait_for_element_to_be_clickable(element)
        
        # time.sleep(2) 
        time.sleep(0.2)
        WebDriverWait(driver,6).until(lambda x: x.find_element(By.CSS_SELECTOR,f'.lazy_fresh_class:nth-child({i+1}) .book_status').is_displayed())
        status = driver.find_element(By.CSS_SELECTOR,status_element).text
        status=status[2:]
        time.sleep(0.5) #added
        # newele=driver.find_element(By.CSS_SELECTOR,element)
        # driver.execute_script("arguments[0].scrollIntoView();", newele)
        # driver.execute_script("arguments[0].click();", newele)
        viewss=driver.find_element(By.CSS_SELECTOR,view_element).get_attribute('innerHTML')
        if viewss[-2:]=='k+':
                viewss=viewss[:-2]+'000'
        elif viewss[-1]=='k':
            viewss=viewss[:-1]+'000'
        elif viewss[-1]=='m':
            viewss=viewss[:-1]+'000000'
        elif viewss[-2:]=='m+':
                viewss=viewss[:-2]+'000000'
        if int(viewss)< 20000:
            i += 1
            # print(i)
            print(viewss,'viewsss')
            prev_book_skip=True
            # ans.append(pd.Series(), ignore_index=True)
            # driver.execute_script("window.scrollTo(0, 0)")
            continue
        driver.find_element(By.CSS_SELECTOR,element).click()  #book opened
        time.sleep(4)#3->4
        WebDriverWait(driver,6).until(lambda x: x.find_element(By.CSS_SELECTOR,'.amoutItem___1_NQS').is_displayed())
        # time.sleep(0.5)
        if start: 
            time.sleep(4)
        soup = bs(driver.page_source,"lxml")
        # print(soup.select_one('.title___2a65l').text)
        try:
            title = get_text(soup,'.title___2a65l')
        except:
            title = "Error"
        try:
            URL = driver.current_url    
            book_id=URL.split('=')[1]
        except:
            URL = "Error"
            book_id = "Error"
        try:
            author = get_text(soup,'.author___1t4Ix span')
        except:
            author = "Error"
        try:
            description = get_text(soup,'.synopsisContent___2OGmq')
        except:
            description = "Error"
        try:
            views = get_text(soup,'.amoutItem___1_NQS:nth-child(1) .anticon+ span')
            if views[-2:]=='k+':
                views=views[:-2]+'000'
            elif views[-1]=='k':
                views=views[:-1]+'000'
            elif views[-1]=='m':
                views=views[:-1]+'000000'
            elif views[-2:]=='m+':
                views=views[:-2]+'000000'
        except:
            views = "Error"
        try:
            likes = get_text(soup,'.amoutItem___1_NQS:nth-child(2) .anticon+ span')
            if likes[-2:]=='k+':
                likes=likes[:-2]+'000'
            elif likes[-1]=='k':
                likes=likes[:-1]+'000'
            elif likes[-1]=='m':
                likes=likes[:-1]+'000000'
            elif likes[-2:]=='m+':
                likes=likes[:-2]+'000000'
        except:
            likes = "Error"
        try:
            genre = get_text(soup,'.amoutItem___1_NQS~ .amoutItem___1_NQS+ .amoutItem___1_NQS .anticon+ span')
        except:
            genre = "Error"
        try:
            tags=[]
            tag_no=1
            while True: #getting all the sub-genre
                try:
                    tag=get_text(soup,f'.tabItem___2Qzp9:nth-child({tag_no}) span:not(.anticon)')
                    tags.append(tag)
                    tag_no+=1
                except:
                    break
        except:
            tags=['Error']
        # #code to find number of chapters
        # read_button='.reading_btn___3zPeA'
        # driver.find_element(By.CSS_SELECTOR,read_button).click()
        # time.sleep(3)  #use until instead of this
        # chapter_catalog='.icon_size_pc'
        # driver.find_element(By.CSS_SELECTOR,chapter_catalog).click()
        # chap_css='.catalogItem___2S-0X'
        # num_chapts=len(driver.find_elements(By.CSS_SELECTOR,chap_css))
        # # print('#############')
        # # print(num_chapts)
        # driver.back()
         
        ans.loc[len(ans.index)] = [title,URL,book_id,author,description,status,views,likes,#num_chapts,
        tags,genre]
        
        ans.to_csv(f"read_write_{categories[c]}.csv",index=False) 
            # ans.to_csv('read_write_YA-Teen.csv',index=False) #/ causes directory issues
            # ans.to_csv(f'tr.csv',index=False)
        i += 1
        driver.back()
        time.sleep(2)
        print(i)
    except Exception as e:
        print("error:",e)
        print('near to element, small scroll')
        driver.execute_script("window.scrollTo(0, window.scrollY+300)") 
        time.sleep(0.3)
# now that full page is loaded w content :) 
# in new driver we open all title links 