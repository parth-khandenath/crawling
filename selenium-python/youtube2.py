import undetected_chromedriver as uc
import pandas as pd
import time
from selenium.webdriver.common.by import By

df_header = {
    "Title" :[],
    "Views":[],
    "Upload date":[]
}

options = uc.ChromeOptions() 
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")

driver = uc.Chrome(options=options)

channel_name="TecentVideo"  #change here

site=f'https://www.youtube.com/@{channel_name}/videos'

ans=pd.DataFrame(df_header)
driver.get(site)
time.sleep(3)
video_no=1

while video_no<7000: #change this number as per total videos of channel
    row_no=video_no//4 +1
    try:
        print("trying row no.",row_no)
        row_titles=driver.find_elements(By.CSS_SELECTOR,f'#contents .ytd-rich-grid-renderer:nth-child({row_no}) #video-title')
        row_views_dates=driver.find_elements(By.CSS_SELECTOR,f'#contents .ytd-rich-grid-renderer:nth-child({row_no}) #metadata-line span')
        for indx in range(len(row_titles)):
            title=row_titles[indx].get_attribute('innerHTML')
            views=row_views_dates[2*indx].get_attribute('innerHTML')
            views=views[:-6]
            date=row_views_dates[2*indx+1].get_attribute('innerHTML')
            if views[-1]=='M':
                if not '.' in views:
                    views=views[:-1]+'000000'
                else:
                    views= float(views[:-1])*1000000
            elif views[-1]=='K':
                if not '.' in views:
                    views=views[:-1]+'000'
                else:
                    views= float(views[:-1])*1000
            if int(views)>=100000: #threshold for views
                ans.loc[len(ans.index)]=[title,views,date]
                ans.to_csv(f'youtube-{channel_name}.csv',index=False) 
        if len(row_titles)<4 and len(row_titles)>0: #this was the last row
            print("last row:", row_no)
            break
        elif len(row_titles)==0:
            print("scroll needed, row no:", row_no)
            driver.execute_script("window.scrollTo(0, window.scrollY+200)")
            continue
        video_no+=4
    except Exception as e:
        print(e)
        print('scrolling down')
        driver.execute_script("window.scrollTo(0, window.scrollY+200)")

print()
print("Process completed......")
print()