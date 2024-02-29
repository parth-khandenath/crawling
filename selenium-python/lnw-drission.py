import time
from DrissionPage import ChromiumPage
from bs4 import BeautifulSoup
from csv import DictWriter
import os

file_name="light-novel-world.csv"
df_header = {'id': [], 'title': [], 'url': [], 'author': [], 'rank': [], 'rating': [], 'views': [],
                          'chapter_count': [], 'bookmarked': [], 'categories': [], 'summary': [], 'tags': []}

def append_list_as_row(list_of_elem):
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
        writer = DictWriter(csvfile, fieldnames=df_header)
        if not file_exists:
            writer.writeheader()
        writer.writerow(list_of_elem)

page=ChromiumPage()
canskip=True
offset=67
for pg in range(1+offset,86):
    page_url=f'https://www.lightnovelworld.co/browse/genre-all-25060123/order-popular/status-all?page={pg}'
    page.get(page_url)
    print('PAGE:',page_url)
    time.sleep(6)
    soup1 = BeautifulSoup(page.html,'lxml')
    # print(soup1)
    link_eles= soup1.select('h4.novel-title a')
    # print(link_eles)
    book_links=[]
    for ele in link_eles:
        book_links.append(ele['href'])
    # print(book_links)
    for bl in book_links:
        id=bl.split('-')[-1]
        if bl[:6] == '/novel':
            book_link='https://www.lightnovelworld.co' + bl
        else:
            book_link=bl
        if book_link=="https://www.lightnovelworld.co/novel/xianxia-my-junior-sisters-are-freaks-25052150":
            canskip=False
        if canskip:
            continue
        page.get(book_link)
        print('BOOK:',book_link)
        time.sleep(3)
        soup2 = BeautifulSoup(page.html,'lxml')
        try:
            title = soup2.select_one('.novel-title').get_text(strip=True)
        except:
            try:
                page.get(book_link)
                time.sleep(6)
                soup2 = BeautifulSoup(page.html,'lxml')
                title = soup2.select_one('.novel-title').get_text(strip=True)
            except:
                title='NA'
        try:
            author = soup2.select_one('div.author a.property-item span').get_text(strip=True)
        except Exception as e:
            print(e)
            author='NA'
        stats = soup2.select('strong')
        rank=stats[0].get_text(strip=True)
        rating=stats[1].get_text(strip=True)
        chapter_count=stats[2].get_text(strip=True)
        views=stats[3].get_text(strip=True)
        bookmarked=stats[4].get_text(strip=True)
        status=stats[5].get_text(strip=True)

        category_eles=soup2.select('li .property-item')
        categories = [ele.get_text(strip=True) for ele in category_eles]

        summary = ''
        p_eles = soup2.select('.summary p')
        for ele in p_eles:
            summary += ele.get_text(strip=True)

        tags = []
        tag_eles = soup2.select('ul.content li')
        for ele in tag_eles:
            tags.append(ele.get_text(strip=True))

        data = {
            'id': 'lightnovelworld-' + id,
            'title': title,
            'url': book_link,
            'author': author,
            'rank': rank,
            'rating': rating,
            'views': views,
            'chapter_count': chapter_count,
            'bookmarked': bookmarked,
            'categories': categories,
            'summary': summary,
            'tags': tags
        }
        append_list_as_row(data)

page.close()