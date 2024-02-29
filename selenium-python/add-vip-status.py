import pandas as pd
import time
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
# .album-cornor.z_i

file_name='ximalaya_City.csv'
df=pd.read_csv('xs/'+file_name)
options = uc.ChromeOptions() 
# options.page_load_strategy = 'eager'
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--headless')
options.add_argument(f"--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36")
driver = uc.Chrome(options=options)

canskip=True
for idx,row in df.iterrows():
    url=row['URL']
    print(url)
    if url=='https://www.ximalaya.com/album/68150025':  #for resuming
        canskip=False
    if canskip:
        continue
    driver.get(url)
    time.sleep(0.2)
    lst=driver.find_elements(By.CSS_SELECTOR,'.album-cornor.z_i')
    if len(lst) > 0:
        print('y')
        df.at[idx, 'vip status'] = 'yes'
    else:
        print('n')
        df.at[idx, 'vip status'] = 'no'
    df.to_csv('xs/'+file_name,index=False)
    