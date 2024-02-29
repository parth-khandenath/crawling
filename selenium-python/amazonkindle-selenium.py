from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from csv import DictWriter
from bs4 import BeautifulSoup
import os
import time
from DrissionPage import ChromiumPage

df_header = {
            "book_name":[],
            "author":[],
            "author_link":[],
            "book_link":[],
            "book_id":[],
            "rating":[],
            "num_of_ratings":[],
            "format":[],
            "price":[],
            "rank":[],
            "percent_4n5stars":[],
            "print_length":[],
            "lang":[],
            "pub_date":[],
            "publisher":[],
            "summary":[]
        }

def append_list_as_row(list_of_elem):
    file_exists = os.path.isfile(filename)
    with open(filename, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
        writer = DictWriter(csvfile, fieldnames=df_header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(list_of_elem)


options=uc.ChromeOptions()
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--cookie=aws-ubid-main=740-7370645-5242451; session-id=131-6894656-6125142; session-id-time=2082787201l; i18n-prefs=USD; sp-cdn="L5Z9:IN"; ubid-main=133-5129884-6918967; skin=noskin; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Asts%3A%3A856517911253%3Aassumed-role%2FAWSReservedSSO_BackInnies_fa60f0f6242afd57%2Fparth.khandenath%40pocketfm.com%22%2C%22alias%22%3A%22radio-ly%22%2C%22username%22%3A%22assumed-role%252FAWSReservedSSO_BackInnies_fa60f0f6242afd57%252Fparth.khandenath%2540pocketfm.com%22%2C%22keybase%22%3A%22vQ99v68c4K02OcaQJMYUnJGG6MnfhVcS7vmqgTLpszE%5Cu003d%22%2C%22issuer%22%3A%22https%3A%2F%2Fpocketfm-apsoutheast-1.awsapps.com%2Fstart%2F%23%2Fsaml%2Fcustom%2F856517911253%2520%2528Radio.ly%2529%2FODU2NTE3OTExMjUzX2lucy05N2JhZTU2YWQ0Mjc4OGNmX3AtMTY2NzEwZmYyZTdiYTJlNg%5Cu003d%5Cu003d%22%2C%22signinType%22%3A%22PUBLIC%22%7D; aws-userInfo-signed=eyJ0eXAiOiJKV1MiLCJrZXlSZWdpb24iOiJhcC1zb3V0aGVhc3QtMSIsImFsZyI6IkVTMzg0Iiwia2lkIjoiNzc2YjdlYTUtODRhYi00N2I0LTg1MmMtMjBhNDJjNjEwYjBlIn0.eyJzdWIiOiJyYWRpby1seSIsInNpZ25pblR5cGUiOiJQVUJMSUMiLCJpc3MiOiJodHRwczpcL1wvcG9ja2V0Zm0tYXBzb3V0aGVhc3QtMS5hd3NhcHBzLmNvbVwvc3RhcnRcLyNcL3NhbWxcL2N1c3RvbVwvODU2NTE3OTExMjUzJTIwJTI4UmFkaW8ubHklMjlcL09EVTJOVEUzT1RFeE1qVXpYMmx1Y3kwNU4ySmhaVFUyWVdRME1qYzRPR05tWDNBdE1UWTJOekV3Wm1ZeVpUZGlZVEpsTmc9PSIsImtleWJhc2UiOiJ2UTk5djY4YzRLMDJPY2FRSk1ZVW5KR0c2TW5maFZjUzd2bXFnVExwc3pFPSIsImFybiI6ImFybjphd3M6c3RzOjo4NTY1MTc5MTEyNTM6YXNzdW1lZC1yb2xlXC9BV1NSZXNlcnZlZFNTT19CYWNrSW5uaWVzX2ZhNjBmMGY2MjQyYWZkNTdcL3BhcnRoLmtoYW5kZW5hdGhAcG9ja2V0Zm0uY29tIiwidXNlcm5hbWUiOiJhc3N1bWVkLXJvbGUlMkZBV1NSZXNlcnZlZFNTT19CYWNrSW5uaWVzX2ZhNjBmMGY2MjQyYWZkNTclMkZwYXJ0aC5raGFuZGVuYXRoJTQwcG9ja2V0Zm0uY29tIn0.IafD94OK7MsDzBgB0hmZhM0lQx5O1qz2PYkf-5lCLhysfZ4uW5Y3GBp6w50FNX9C5POzNNed4lIduH0S64YlUfIGsVIY1ytpqckFj41Ba-3n2YLA7ZhX9wZkzQ1-Ecek; noflush_awsccs_sid=bb5b846d0805b435693bebe569b4f935c25378d840435f35351e727e04b7e582; lc-main=en_US; session-token=/5zE8qmQvWRorYm93rvkhHJ3dE1HFNK4LJQx2/rbrMLAbGMMfkguUmGktPgShkLjy/O5ICvn+c1+nBRs5MK/OO5E3ELThvQQhxJFDsKlQ8tVrIPpnCocJUEPOk/GQnZOzPviWCJMdxGqu/lDUOKMsIP8Pm4XHtAlP1foSOZs1H4J1n79gqBM+gfL1MG/H+a7Rq9xm4WKUrt4HB0UzjoTKpNJ3Sqo7/J0uQHHwAs4aDM0epT/Yn26n40IKvvnnd1+lGPl9DODhlKDNaadrEZLIyZzDbbVcUWbPhHsjOVwp0Ks1jMb4Gc7Me/EijPa4g+n06RjQhveoDmSDj+NLYER1J2eS8e7bGud; csm-hit=tb:s-GFV49DPRXHZCWD2PEXAD|1709126625818&t:1709126626268&adb:adblk_no')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36')
# driver = uc.Chrome(options=options)
page=ChromiumPage()

#change below 2
start_url="https://www.amazon.com/Best-Sellers-Kindle-Store-Fantasy/zgbs/digital-text/158576011/ref=zg_bs_pg_1_digital-text?_encoding=UTF8"
filename="new-fantasy-top100-paid.csv"

for pg in range(2):
    print("PAGE:",pg)
    # driver.get(start_url+"&pg="+str(pg+1))
    page.get(start_url+"&pg="+str(pg+1))
    time.sleep(4)
    # for _ in range(2):
    #     print('scrolling')
    #     driver.execute_script("window.scrollTo(0, window.scrollY+6000)")
    time.sleep(6)
    # soup=BeautifulSoup(driver.page_source,'lxml')
    soup=BeautifulSoup(page.html,'lxml')
    book_eles = soup.select("div._cDEzb_iveVideoWrapper_JJ34T")
    # ranks = soup.select("span.zg-bdg-text")
    print(len(book_eles))
    # print(len(ranks))
    # continue
    i = 0
    for ele in book_eles:
        i += 1
        print(i)
        # if i<=30 or i>=39:
        #     continue
        try:
            book_name = ele.select_one("a.a-link-normal ._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y").text
        except:
            book_name="NA"
        try:
            author = ele.select_one("a.a-link-child ._cDEzb_p13n-sc-css-line-clamp-1_1Fn1y").text
        except:
            author="NA"
        try:
            author_link = "https://www.amazon.com" + ele.select_one("a.a-link-child")['href']
        except:
            author_link="NA"
        try:
            book_link = "https://www.amazon.com" + ele.select_one("a.a-link-normal")['href']
        except:
            book_link="NA"
        book_id = book_link.split('/')[-3]
        try:
            rating = ele.select_one(".a-icon-row .a-link-normal")['title']
        except:
            rating="NA"
        try:
            num_of_ratings = ele.select_one("span.a-size-small").text
        except:
            num_of_ratings="NA"
        try:
            book_format = ele.select_one("span.a-text-normal").text
        except:
            book_format="NA"
        try:
            price = ele.select_one("span._cDEzb_p13n-sc-price_3mJ9Z").text
        except:
            price="NA"
        # try:
        #     rank = 50*(pg)+i #ranks[i].text
        # except:
        #     rank="NA"

        # driver.get(book_link)
        page.get(book_link)
        print(book_link)
        time.sleep(1.5)
        print('scrolling')
        # driver.execute_script("window.scrollTo(0, window.scrollY+6000)")
        time.sleep(1.5)
        # soup2=BeautifulSoup(driver.page_source,'lxml')
        soup2=BeautifulSoup(page.html,'lxml')
        percents = soup2.select("#histogramTable .a-text-right .a-size-base")
        percent5star = int(percents[0].text[:-1])
        percent4star = int(percents[1].text[:-1])
        percent_4n5stars = f"{str(percent5star + percent4star)}%"

        vals=soup2.select("#detailBullets_feature_div li span:not(.a-text-bold):not(.a-list-item)")
        keys=soup2.select("#detailBullets_feature_div li span.a-text-bold")

        publisher="NA"
        print_length = "NA"
        lang = "NA"
        pub_date = "NA"
        publisher = "NA"
        bestseller_rank="NA"

        for j in range(len(keys)):
            if "Publisher" in keys[j].text:
                publisher=vals[j].text
            elif "Publication date" in keys[j].text:
                pub_date=vals[j].text
            elif "Language" in keys[j].text:
                lang=vals[j].text
            elif "Print length" in keys[j].text:
                print_length=vals[j].text

        # rank_eles=soup2.select("#detailBullets_feature_div+ .detail-bullet-list li")
        # rank=[]
        # for ele in rank_eles:
        #     rank.append(ele.text)
        rank=soup2.select_one("#detailBullets_feature_div+ .detail-bullet-list li").text
        
        try:
            summary = soup2.select_one(".a-expander-content-expanded span").text
        except:
            try:
                summary=soup2.select_one(".a-expander-partial-collapse-content").text
            except:
                try:
                    summary=soup2.select_one("#bookDescription_feature_div p").text
                except:
                    summary="NA"

        data = {
            "book_name": book_name,
            "author": author,
            "author_link": author_link,
            "book_link": book_link,
            "book_id": 'amazonkindle-'+book_id,
            "rating": rating,
            "num_of_ratings": num_of_ratings,
            "format": book_format,
            "price": price,
            "rank": rank,
            "percent_4n5stars":percent_4n5stars,
            "print_length":print_length,
            "lang":lang,
            "pub_date":pub_date,
            "publisher":publisher,
            "summary":summary
        }
        # print(data)
        # break
        append_list_as_row(data)

page.close()   
# driver.quit()
# driver.close()