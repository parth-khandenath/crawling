import re
import time
import pandas as pd
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Initialize WebDriver (Chrome in this example)
options=uc.ChromeOptions()
options.page_load_strategy='eager'
driver = uc.Chrome()

# Base URL
start_url = 'https://www.novelupdates.com/genre/horror/?sort=4&order=2&status=1&pg=1'

# CSV file name
filename = 'novelupdates-horror.csv'

# Data headers
df_headers = {
    "Title": [],
    "numOfChps": [],
    "status": [],
    "lastepisode": [],  
    "Tags": [],
    "url": [],
    "description": [],
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
    "original publisher": [],
    "english publisher": [],
    "release frequency": [],
    "readers": [],
    "reading list rank": [],
    "reviews": [],
    'activity status rank':[]
}

# Try to read the existing CSV file or create a new DataFrame
try:
    ans = pd.read_csv(f'{filename}.csv')
except:
    ans = pd.DataFrame(df_headers)

# Function to parse the book details page
def parse_book(url, meta,page):
    print(page)
    print('book:',url)
    driver.get(url)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    desc = soup.select_one('#editdescription p').text.strip() if soup.select_one('#editdescription p') else 'NA'
    type_ = soup.select_one('#showtype').text.strip() if soup.select_one('#showtype') else 'NA'
    genre = '-'.join([g.text for g in soup.select('#seriesgenre .genre')])
    tags2 = '-'.join([t.text for t in soup.select('#etagme')])
    rating_split = ''
    for r in soup.select('table#myrates tr'):
        rating_split += f"{r.select_one('.rating').text}:{r.select_one('.votetext').text} "
    votes = soup.select_one("#taghidemsg+ .seriesother .uvotes").text.replace('(','').replace(')','').split(',')[1] if soup.select_one("#taghidemsg+ .seriesother .uvotes") else 'NA'
    votes=votes.replace('votes','')
    rating = soup.select_one("#taghidemsg+ .seriesother .uvotes").text.replace('(','').replace(')','').split(',')[0].split('/')[0] if soup.select_one("#taghidemsg+ .seriesother .uvotes") else 'NA'
    lang = soup.select_one('#showlang').text.strip() if soup.select_one('#showlang') else 'NA'
    author = soup.select_one('#showauthors').text.strip() if soup.select_one('#showauthors') else 'NA'
    artist = soup.select_one('#showartists').text.strip() if soup.select_one('#showartists') else 'NA'
    year = soup.select_one("#edityear").text.strip() if soup.select_one("#edityear") else 'NA'
    orig_pub = soup.select_one("#showopublisher").text.strip() if soup.select_one("#showopublisher") else 'NA'
    eng_pub = soup.select_one("#myepub").text.strip() if soup.select_one("#myepub") else 'NA'
    
    rlrank = ''
    acsr = ''

    weekly_rank = soup.select('h5.seriesother ~ span.userrate.rank')[0].text if soup.select('h5.seriesother ~ span.userrate.rank')[0] else 'NA'
    monthly_rank = soup.select('h5.seriesother ~ span.userrate.rank')[1].text if soup.select('h5.seriesother ~ span.userrate.rank')[1] else 'NA'
    all_time_rank = soup.select('h5.seriesother ~ span.userrate.rank')[2].text if soup.select('h5.seriesother ~ span.userrate.rank')[2] else 'NA'
    
    acsr += f'weekly: {weekly_rank}, monthly: {monthly_rank}, all time: {all_time_rank}'

    reading_lists_monthly_rank = soup.select('b.rlist ~ span.userrate.rank')[0].text if soup.select('b.rlist ~ span.userrate.rank')[0] else 'NA'
    reading_lists_all_time_rank = soup.select('b.rlist ~ span.userrate.rank')[1].text if soup.select('b.rlist ~ span.userrate.rank')[1] else 'NA'
    
    rlrank += f'monthly: {reading_lists_monthly_rank}, all time: {reading_lists_all_time_rank}'

    ans.loc[len(ans.index)] = [
        meta['title'], meta['chaps'], meta['status'], meta['lastepi'], meta['tags'], meta['url'], desc, type_, genre, tags2, rating_split, rating, votes, lang, author, artist, year, orig_pub, eng_pub, meta['freq'], meta['reads'], rlrank, meta['revs'], acsr
    ]

    ans.to_csv(f"{filename}.csv", index=False)

# Function to parse the main genre page
def parse_page(page_url,page):
    if page<29:
        return
    canskip=(page==29)
    driver.get(page_url)
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    titles = [e.text for e in soup.select('.search_title a')]
    urls = [e['href'] for e in  soup.select('.search_title a')]
    chapss = [e.text for e in soup.select('.ss_desk:nth-child(1)')]
    freqs = [e.text for e in soup.select('.ss_desk:nth-child(2)')]
    readss = [e.text for e in soup.select('.ss_desk:nth-child(3)')]
    revss = [e.text for e in soup.select('.ss_desk:nth-child(4)')]
    statuss = ['NA']*25
    lastepis = [e.text for e in soup.select('.ss_desk:nth-child(5)')]
    tagss=[]
    for i,ele in enumerate(soup.select('.search_genre')):
        tgs=[]
        for t in ele:
            if 'Completed' in t.text:
                statuss[i]='Completed'
            else:
                tgs.append(t.text)
        tagss.append('-'.join(tgs))
    for i in range(len(urls)):
        if urls[i]=='https://www.novelupdates.com/series/boogiepop-missing-peppermint-no-majutsushi/':
            canskip=False
        if canskip:
            continue
        meta = {
            'title': titles[i],
            'chaps': (chapss[i]).replace('Chapters',''),
            'status': statuss[i],
            'lastepi': lastepis[i],
            'tags': tagss[i],
            'url': urls[i],
            'freq': freqs[i],
            'reads': (readss[i]).replace('Readers',''),
            'revs': (revss[i]).replace('Reviews','')
        }
        parse_book(urls[i], meta,page)
        time.sleep(2)# Add delay to avoid being blocked

# Iterate over multiple pages
for i in range(29, 30):
    print('PAGE:',i)
    page_url = f"https://www.novelupdates.com/genre/horror/?sort=4&order=2&status=1&pg={i}"
    print(page_url)
    parse_page(page_url,i)
    # time.sleep(2)  # Add delay to avoid being blocked

# Close the driver
driver.quit()
driver.close()