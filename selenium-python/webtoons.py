import requests
import pandas as pd
from bs4 import BeautifulSoup as bs
import time
import re

url = "https://www.webtoons.com/en/dailySchedule"

response = requests.get(url)

genre_list = []
title_list = []
episodes_list = []
view_list = []
subscription_list = []
rating_list = []
status_list = []
indication_list = []
url_list = []


def get_book_details(url, idx):
    res = requests.get(url)
    soup =bs(res.text,"lxml")

    genre = soup.find('h2', class_="genre").text.strip()
    title = soup.find('h1', class_="subj").text.strip()

    ul_tag = soup.find('div', {'id' : '_asideDetail'}).find('ul', class_="grade_area")
    li_tags = ul_tag.find_all('li')
    views = ""
    subscribers = ""
    rating = ""
    for i in range(0, 3):
        if i == 0:
            views = li_tags[i].find('em', class_="cnt").text.strip()
        elif i == 1:
            subscribers = li_tags[i].find('em', class_="cnt").text.strip()
        elif i == 2:
            rating = li_tags[i].find('em', class_="cnt").text.strip()

    status = ""
    if idx <= 7:
        status = soup.find('p', class_="day_info").find('span', class_="txt_ico_up").text.strip()
        status = status + " --- " + soup.find('p', class_="day_info").text.strip()

    elif idx == 8:
        status = soup.find('p', class_="day_info").text.strip()

    indication = ""
    try:
        div_tag = soup.find('div', class_="detail_lst").find('div', class_="detail_install_app")
        indication = div_tag.find('strong').text.strip()
    except Exception as e:
        print("No Indication in this link")

    episodes = soup.find('ul', {'id': '_listUl'}).find_all('li')
    episodes = episodes[0].find('span', class_="subj").find('span').text.strip()

    url_list.append(url)
    episodes_list.append(episodes)
    indication_list.append(indication)
    status_list.append(status)
    view_list.append(views)
    subscription_list.append(subscribers)
    rating_list.append(rating)
    title_list.append(title)
    genre_list.append(genre)


soup=bs(response.text,"lxml")

for i in range(1, 9):
    day_str = ""
    daily_section = ""
    if i == 1:
        day_str = "daily_section _list_MONDAY"
    elif i == 2:
        day_str = "daily_section _list_TUESDAY"
    elif i == 3:
        day_str = "daily_section _list_WEDNESDAY"
    elif i == 4:
        day_str = "daily_section _list_THURSDAY"
    elif i == 5:
        day_str = "daily_section _list_FRIDAY"
    elif i == 6:
        day_str = "daily_section _list_SATURDAY"
    elif i == 7:
        day_str = "daily_section _list_SUNDAY"

    if i <= 7: #this is for ongoing series
        daily_section = soup.find('div', class_= day_str)
    elif i == 8: #this is for completed series
        daily_section = soup.find('div', class_="daily_section on")

    ul_tag = daily_section.find('ul', class_="daily_card")
    li_tags = ul_tag.find_all('li')

    for li in li_tags:
        book_url = li.find('a')['href']
        get_book_details(book_url, i)

    print(f'Week {i} Done!')

df = pd.DataFrame({
    'Title': title_list,
    'Genre': genre_list,
    'Episodes': episodes_list,
    'View': view_list,
    'Subscribers': subscription_list,
    'Ratings': rating_list,
    'Status': status_list,
    'Indication': indication_list,
    'URL': url_list
})

df.to_csv("Webtoons Data.csv", index=False)