import undetected_chromedriver as uc
from bs4 import BeautifulSoup as bs
import time
from selenium.webdriver.common.by import By
import os
import requests
import json
from csv import DictWriter


# COLUMNS = ["ISBN", "Title", "Ratings", "No. of Ratings", "URL","No"]
COLUMNS = ["book_id","title","ageGrade","total_chaps","rating","views","tags","genre","description","url","publisher","chapter1_date"]
def append_list_as_row(file_name, list_of_elem):
    file_exists = os.path.isfile(file_name)
    with open(file_name, mode="a+", encoding="utf-8-sig", newline="") as csvfile:
        writer = DictWriter(csvfile, fieldnames=COLUMNS)
        if not file_exists:
            writer.writeheader()
        writer.writerow(list_of_elem)
def filter_data(book_data):
    for key in book_data.keys():
        if not book_data[key]:
            book_data[key] = "NA"
    return book_data
def fill_data(book_data, tag, info):
    if book_data[tag]:
        book_data[tag] +=info 
    else:
        book_data[tag] = info
    return book_data
def get_payload(page):
    json_data={"query":"\n    query staticLandingGenreSection($sectionId: ID!, $param: StaticLandingGenreParamInput!) {\n  staticLandingGenreSection(sectionId: $sectionId, param: $param) {\n    ...Section\n  }\n}\n    \n    fragment Section on Section {\n  id\n  uid\n  type\n  title\n  ... on CardSection {\n    isRecommendArea\n    isRecommendedItems\n  }\n  ... on DependOnLoggedInSection {\n    loggedInTitle\n    loggedInScheme\n  }\n  ... on SchemeSection {\n    scheme\n  }\n  ... on MetaInfoTypeSection {\n    metaInfoType\n  }\n  ... on TabSection {\n    sectionMainTabList {\n      uid\n      title\n      isSelected\n      scheme\n      additionalString\n      subTabList {\n        uid\n        title\n        isSelected\n        groupId\n      }\n    }\n  }\n  ... on ThemeKeywordSection {\n    themeKeywordList {\n      uid\n      title\n      scheme\n    }\n  }\n  ... on StaticLandingDayOfWeekSection {\n    isEnd\n    totalCount\n    param {\n      categoryUid\n      businessModel {\n        name\n        param\n      }\n      subcategory {\n        name\n        param\n      }\n      dayTab {\n        name\n        param\n      }\n      page\n      size\n      screenUid\n    }\n    businessModelList {\n      name\n      param\n    }\n    subcategoryList {\n      name\n      param\n    }\n    dayTabList {\n      name\n      param\n    }\n    promotionBanner {\n      ...PromotionBannerItem\n    }\n  }\n  ... on StaticLandingTodayNewSection {\n    totalCount\n    param {\n      categoryUid\n      subcategory {\n        name\n        param\n      }\n      screenUid\n    }\n    categoryTabList {\n      name\n      param\n    }\n    subcategoryList {\n      name\n      param\n    }\n    promotionBanner {\n      ...PromotionBannerItem\n    }\n    viewType\n  }\n  ... on StaticLandingTodayUpSection {\n    isEnd\n    totalCount\n    param {\n      categoryUid\n      subcategory {\n        name\n        param\n      }\n      page\n    }\n    categoryTabList {\n      name\n      param\n    }\n    subcategoryList {\n      name\n      param\n    }\n  }\n  ... on StaticLandingRankingSection {\n    isEnd\n    rankingTime\n    totalCount\n    param {\n      categoryUid\n      subcategory {\n        name\n        param\n      }\n      rankingType {\n        name\n        param\n      }\n      page\n      screenUid\n    }\n    categoryTabList {\n      name\n      param\n    }\n    subcategoryList {\n      name\n      param\n    }\n    rankingTypeList {\n      name\n      param\n    }\n    displayAd {\n      ...DisplayAd\n    }\n    promotionBanner {\n      ...PromotionBannerItem\n    }\n    withOperationArea\n    viewType\n  }\n  ... on StaticLandingGenreSection {\n    isEnd\n    totalCount\n    param {\n      categoryUid\n      subcategory {\n        name\n        param\n      }\n      sortType {\n        name\n        param\n      }\n      page\n      isComplete\n      screenUid\n    }\n    subcategoryList {\n      name\n      param\n    }\n    sortTypeList {\n      name\n      param\n    }\n    displayAd {\n      ...DisplayAd\n    }\n    promotionBanner {\n      ...PromotionBannerItem\n    }\n  }\n  ... on StaticLandingFreeSeriesSection {\n    isEnd\n    totalCount\n    param {\n      categoryUid\n      tab {\n        name\n        param\n      }\n      page\n      screenUid\n    }\n    tabList {\n      name\n      param\n    }\n    promotionBanner {\n      ...PromotionBannerItem\n    }\n  }\n  ... on StaticLandingEventSection {\n    isEnd\n    totalCount\n    param {\n      categoryUid\n      page\n    }\n    categoryTabList {\n      name\n      param\n    }\n  }\n  ... on StaticLandingOriginalSection {\n    isEnd\n    totalCount\n    originalCount\n    param {\n      categoryUid\n      subcategory {\n        name\n        param\n      }\n      sortType {\n        name\n        param\n      }\n      isComplete\n      page\n      screenUid\n    }\n    subcategoryList {\n      name\n      param\n    }\n    sortTypeList {\n      name\n      param\n    }\n    recommendItemList {\n      ...Item\n    }\n  }\n  groups {\n    ...Group\n  }\n}\n    \n\n    fragment PromotionBannerItem on PromotionBannerItem {\n  title\n  scheme\n  leftImage\n  rightImage\n  eventLog {\n    ...EventLogFragment\n  }\n}\n    \n\n    fragment EventLogFragment on EventLog {\n  fromGraphql\n  click {\n    layer1\n    layer2\n    setnum\n    ordnum\n    copy\n    imp_id\n    imp_provider\n  }\n  eventMeta {\n    id\n    name\n    subcategory\n    category\n    series\n    provider\n    series_id\n    type\n  }\n  viewimp_contents {\n    type\n    name\n    id\n    imp_area_ordnum\n    imp_id\n    imp_provider\n    imp_type\n    layer1\n    layer2\n  }\n  customProps {\n    landing_path\n    view_type\n    helix_id\n    helix_yn\n    helix_seed\n    content_cnt\n    event_series_id\n    event_ticket_type\n    play_url\n    banner_uid\n  }\n}\n    \n\n    fragment DisplayAd on DisplayAd {\n  sectionUid\n  bannerUid\n  treviUid\n  momentUid\n}\n    \n\n    fragment Item on Item {\n  id\n  type\n  ...BannerItem\n  ...OnAirItem\n  ...CardViewItem\n  ...CleanViewItem\n  ... on DisplayAdItem {\n    displayAd {\n      ...DisplayAd\n    }\n  }\n  ...PosterViewItem\n  ...StrategyViewItem\n  ...RankingListViewItem\n  ...NormalListViewItem\n  ...MoreItem\n  ...EventBannerItem\n  ...PromotionBannerItem\n  ...LineBannerItem\n}\n    \n\n    fragment BannerItem on BannerItem {\n  bannerType\n  bannerViewType\n  thumbnail\n  videoUrl\n  badgeList\n  statusBadge\n  titleImage\n  title\n  altText\n  metaList\n  caption\n  scheme\n  seriesId\n  eventLog {\n    ...EventLogFragment\n  }\n  moreButton {\n    ...MoreButtonFragment\n  }\n}\n    \n\n    fragment MoreButtonFragment on MoreButton {\n  type\n  scheme\n  title\n}\n    \n\n    fragment OnAirItem on OnAirItem {\n  thumbnail\n  videoUrl\n  titleImage\n  title\n  subtitleList\n  caption\n  scheme\n}\n    \n\n    fragment CardViewItem on CardViewItem {\n  title\n  altText\n  thumbnail\n  titleImage\n  scheme\n  badgeList\n  ageGradeBadge\n  statusBadge\n  ageGrade\n  selfCensorship\n  subtitleList\n  caption\n  rank\n  rankVariation\n  isEventBanner\n  categoryType\n  eventLog {\n    ...EventLogFragment\n  }\n}\n    \n\n    fragment CleanViewItem on CleanViewItem {\n  id\n  type\n  showPlayerIcon\n  scheme\n  title\n  thumbnail\n  badgeList\n  ageGradeBadge\n  statusBadge\n  subtitleList\n  rank\n  ageGrade\n  selfCensorship\n  eventLog {\n    ...EventLogFragment\n  }\n}\n    \n\n    fragment PosterViewItem on PosterViewItem {\n  id\n  type\n  showPlayerIcon\n  scheme\n  title\n  altText\n  thumbnail\n  badgeList\n  ageGradeBadge\n  statusBadge\n  subtitleList\n  rank\n  rankVariation\n  ageGrade\n  selfCensorship\n  eventLog {\n    ...EventLogFragment\n  }\n  seriesId\n}\n    \n\n    fragment StrategyViewItem on StrategyViewItem {\n  id\n  title\n  count\n  scheme\n}\n    \n\n    fragment RankingListViewItem on RankingListViewItem {\n  title\n  thumbnail\n  badgeList\n  ageGradeBadge\n  statusBadge\n  ageGrade\n  selfCensorship\n  metaList\n  descriptionList\n  scheme\n  rank\n  eventLog {\n    ...EventLogFragment\n  }\n}\n    \n\n    fragment NormalListViewItem on NormalListViewItem {\n  id\n  type\n  altText\n  ticketUid\n  thumbnail\n  badgeList\n  ageGradeBadge\n  statusBadge\n  ageGrade\n  isAlaramOn\n  row1\n  row2\n  row3 {\n    id\n    metaList\n  }\n  row4\n  row5\n  scheme\n  continueScheme\n  nextProductScheme\n  continueData {\n    ...ContinueInfoFragment\n  }\n  seriesId\n  isCheckMode\n  isChecked\n  isReceived\n  showPlayerIcon\n  rank\n  isSingle\n  singleSlideType\n  ageGrade\n  selfCensorship\n  eventLog {\n    ...EventLogFragment\n  }\n  giftEventLog {\n    ...EventLogFragment\n  }\n}\n    \n\n    fragment ContinueInfoFragment on ContinueInfo {\n  title\n  isFree\n  productId\n  lastReadProductId\n  scheme\n  continueProductType\n  hasNewSingle\n  hasUnreadSingle\n}\n    \n\n    fragment MoreItem on MoreItem {\n  id\n  scheme\n  title\n}\n    \n\n    fragment EventBannerItem on EventBannerItem {\n  bannerType\n  thumbnail\n  videoUrl\n  titleImage\n  title\n  subtitleList\n  caption\n  scheme\n  eventLog {\n    ...EventLogFragment\n  }\n}\n    \n\n    fragment LineBannerItem on LineBannerItem {\n  title\n  scheme\n  subTitle\n  bgColor\n  rightImage\n  eventLog {\n    ...EventLogFragment\n  }\n}\n    \n\n    fragment Group on Group {\n  id\n  ... on ListViewGroup {\n    meta {\n      title\n      count\n    }\n  }\n  ... on CardViewGroup {\n    meta {\n      title\n      count\n    }\n  }\n  ... on PosterViewGroup {\n    meta {\n      title\n      count\n    }\n  }\n  type\n  dataKey\n  groups {\n    ...GroupInGroup\n  }\n  items {\n    ...Item\n  }\n}\n    \n\n    fragment GroupInGroup on Group {\n  id\n  type\n  dataKey\n  items {\n    ...Item\n  }\n  ... on ListViewGroup {\n    meta {\n      title\n      count\n    }\n  }\n  ... on CardViewGroup {\n    meta {\n      title\n      count\n    }\n  }\n  ... on PosterViewGroup {\n    meta {\n      title\n      count\n    }\n  }\n}\n    ","variables":{"sectionId":"static-landing-Genre-section-Layout-11-89-update-false-84",
    "param":{"categoryUid":11,"subcategoryUid":subcat_uid,"sortType":"update","isComplete":False,"screenUid":84,"page":page}}}
    payload = json.dumps(json_data)
    return payload

genre_map={'89':'romance','86':'fantasy','117':'ropan','125':'drama'}

# subcat_uid='117' #change here
subcat_uid='125' #change here
data_file_name = f"kakao-{genre_map[subcat_uid]}.csv"
main_url = "https://page.kakao.com/graphql"
headers = {
  'authority': 'page.kakao.com',
  'accept': 'application/graphql+json, application/json',
  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
  'content-type': 'application/json',
  'cookie': '_kpdid=09c1e5784fc6478994c04ff04c092e5b; _kpiid=bb367  fa490bc82b7fd585f1b1b782703; _ga=GA1.3.1854168541.1704299477; _ga_EGMMPXGJS3=GGS1.3.1704341794.3.1.1704341823.0.0.0; _T_ANO=AytawaWX9TVNax7mpOcV6MSOkcpuZxhEZrSHtoCeIHpbo+cY5dwntk/ECEf/GouYQXDtMj8VlIhX1BYzSH8zyP+ZmGyU541EUFb/P6t3KbdDxz7COZ/9GhdNGEQeOQy2lHm1GtaKFwpz9UDIyyH6bvfta1zw/3p6BxJOvlh6oL2Spws+n/YkqYpKNekrFxv0+JDCwoJ1f/kD5qcdLYgfeUq7vOlBuamEG2WsK8KPyXrToEkNgx2bGUj2ym/HooORJ//ulRY/VnyqowWc4K3b9L0FK9eqNazmMzuvOxkn6PP/LIl6Fq15jI+w7diC257ahKgtVQ8+hYK0Up5iTsyx1g==',
  'origin': 'https://page.kakao.com',
  'referer': f'https://page.kakao.com/menu/10011/screen/84?subcategory_uid={subcat_uid}',
  'sec-ch-ua': '"Google Chrome";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
  'sec-ch-ua-mobile': '?0',
  'sec-ch-ua-platform': '"Windows"',
  'sec-fetch-dest': 'empty',
  'sec-fetch-mode': 'cors',
  'sec-fetch-site': 'same-origin',
  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

driver=uc.Chrome()
# page_no=0    
page_no=168 #resume here
while True:
    try:
        payload=get_payload(page_no)
        response = requests.request("POST", main_url, headers=headers, data=payload)
        # print(response.text)
        if response.status_code!=200:
            print("breaking on page:",page_no)
            break
        res=json.loads(response.text)
        # print(res["data"]["staticLandingRankingSection"]["groups"]["items"])
        for d in res["data"]["staticLandingGenreSection"]["groups"][0]["items"]:
            
            book_id=d["eventLog"]["eventMeta"]["id"]
            book_url=f'https://page.kakao.com/content/{book_id}'
            # ranking=d["rank"]
            title=d["title"]
            genre=d["eventLog"]["eventMeta"]["subcategory"]
            views=d["subtitleList"][0]
            ageGrade=d["ageGrade"]
            try:
                driver.get(book_url)
                time.sleep(2)
                s=bs(driver.page_source,"lxml")
                # print(s)
                # first_chapter_date=s.find(By.CSS_SELECTOR,'.list-child-item:nth-child(1) .h-16pxr .align-middle').text
                # print(first_chapter_date)
                # spans1=s.find_all("span",class_='text-el-70')
                total_chaps=s.select("span.break-all")[5].text
                spans=s.select("span.text-el-70.opacity-70")
                dates=s.select("div.h-16pxr.text-el-50 span.align-middle")
                first_chapter_date=dates[0].text
                print(book_url)
                # print("1:")
                total_chaps=(total_chaps).split()[1]
                # print("2:")
                # print(s.text)
                # divs=s.find_all("div",class_="bg-bg-a-20")
                # total_chaps=s.select_one(By.CSS_SELECTOR,'.rounded-b-12pxr .font-small2-bold.text-el-70').text
                # for d in divs:
                #     if "전체" in d.text:
                #         total_chaps=d.find("span").text
                #         break
                # views=spans[1].text
                # if views[-1]=='억':
                #     views=float(views[:-1])*100000000
                # print("3:")
                rating=spans[2].text
                # print("4:")
                # status="True"
                # for s in spans:
                #     if " 연재" in s.text:
                #         status="False"
                #         break
                # author=spans[-1].text
                
                # for s in spans:
                #     print(s.text)

                
                driver.get(book_url+"?tab_type=about")
                time.sleep(2)
                s1=bs(driver.page_source,"lxml")
                intro=s1.find("span",class_="whitespace-pre-wrap").text
                # print("5:")
                # divs=s1.find_all("div",class_="mt-16pxr")[2].find_all("div")
                tags_ele=s1.select("span.font-small2-bold.text-ellipsis")
                tags=[]
                for ele in tags_ele:
                    tags.append(ele.text)
                # print('(#########)')
                # print("6")
                publisher='N/A'
                divs=s1.select('.pt-6pxr')
                for d in divs:
                    if '발행자' in d.text:
                        publisher =(d.text)[3:]
                        break
                # print("7:",publisher)
                        
                # print(ranking,title,total_chaps,rating,views,tags,genre,book_url,publisher)
                book_data=dict.fromkeys(COLUMNS)
                # book_data["ranking"]=ranking
                book_data["title"]=title
                book_data["book_id"]=book_id
                book_data["ageGrade"]=ageGrade
                book_data["total_chaps"]=total_chaps
                book_data["rating"]=rating
                book_data["views"]=views
                # book_data["status"]=status
                book_data["tags"]=tags
                book_data["genre"]=genre
                book_data["description"]=intro
                book_data["url"]=book_url   
                book_data["publisher"]=publisher
                book_data["chapter1_date"]=first_chapter_date
                append_list_as_row(data_file_name,book_data)   

            except Exception as e:
                print("err:",e)
                print(ageGrade)
                book_data=dict.fromkeys(COLUMNS)
                # book_data["ranking"]=ranking
                book_data["title"]=title
                book_data["book_id"]=book_id
                book_data["ageGrade"]=ageGrade
                book_data["views"]=views
                book_data["genre"]=genre
                book_data["url"]=book_url
                filter_data(book_data)
                append_list_as_row(data_file_name,book_data)
        print("page done:",page_no)
        page_no+=1
    except TimeoutError:
        print("timeout,retrying...")
        time.sleep(20)