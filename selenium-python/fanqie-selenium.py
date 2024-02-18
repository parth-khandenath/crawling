import time
from bs4 import BeautifulSoup as bs
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd

options = uc.ChromeOptions() 

driver = uc.Chrome(options=options)

df_header={'title':[], 'author':[], 'words':[], 'reads':[], 'description':[]}
filename='fanqie-male-minimal.csv'
try:
    df=pd.read_csv(filename)
except:
    df=pd.DataFrame(df_header)

page=1
while page<=99:
    print('page: ',page)
    driver.get(f'https://fanqienovel.com/library/audience1/page_{page}?sort=hottes')
    time.sleep(4)

    titles = driver.find_elements(By.CSS_SELECTOR,'.book-item-title')
    info = driver.find_elements(By.CSS_SELECTOR,'span.font-fKts9tCXDjS49UhH')  #author, write, read
    # authors = driver.find_elements(By.CSS_SELECTOR,'.book-item-desc .font-fKts9tCXDjS49UhH font font')
    # wcs = driver.find_elements(By.CSS_SELECTOR,'.font-fKts9tCXDjS49UhH:nth-child(2)')
    # rcs = driver.find_elements(By.CSS_SELECTOR,'.font-fKts9tCXDjS49UhH~ .font-fKts9tCXDjS49UhH ') #ignore even (1 based indexing)
    descs = driver.find_elements(By.CSS_SELECTOR,'.book-item-abstract')
    # print(titles)
    # print(info)
    # print(descs)
    for i in range(len(titles)):
        t=titles[i].text
        a=info[3*i].text
        w=info[3*i+1].text
        r=info[3*i+2].text
        d=descs[i].text
        print()
        print([t,a,w,r,d])
        print()
        df.loc[len(df.index)]=[t,a,w,r,d]
        # ans.loc[len(ans.index)]
        df.to_csv(filename,index=False)

    page+=1