from datetime import datetime, timedelta
from selenium import webdriver
import time
import bs4
import requests
import re
import json
# def Scroll_window(): #滾動視窗到最底端(為了加載更新讓舊的評論出現)
#     browser.execute_script("window.scrollTo(0, document.body.scrollHeight)")

# def Prompt_Window(): #判斷是否出現'是否繼續使用網頁版視窗'，有的話點擊繼續使用。
#     try:
#         btn=browser.find_element_by_xpath("//button[contains(text(),'繼續用網頁版')]")
#         print("彈出是否繼續視窗")
#         btn.click()
#     except:
#         print("沒有彈出視窗")

def find_stock_ID(): #找尋公司在網頁的特定ID
    stock_url=browser.current_url
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    stock_html=requests.get(stock_url,headers=headers)
    objsoup=bs4.BeautifulSoup(stock_html.text,'lxml')
    Find_Id=objsoup.find('div',id="PageData").text
    pattern = r'\"ChannelId\"\:\"\d*\"'
    Channel_Id=list(re.search(pattern,Find_Id).group())[13:-1]
    ChannelId="".join(Channel_Id)
    return ChannelId
stock=input("輸入要找的股票公司")

options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument('headless')
dirverPath='C:\webdriver\chromedriver.exe'
browser = webdriver.Chrome(dirverPath,options=options)


url='https://www.cmoney.tw/follow/channel/'
browser.get(url)

search=browser.find_element_by_xpath("//input[@id='TopSide-TxtSearch']")
search.send_keys(stock)
time.sleep(3)
search.submit()
time.sleep(3)

channelId=find_stock_ID()
size=500 #讀取前n筆評論(最多500)
cmoney_content_url='https://www.cmoney.tw/follow/channel/getdata/articlelistofstockv2?articleCategory=Personal&channelId=%s&size=%s&sTime=&articleSortType=latest&articleSortCount=0&isIncludeLimitedAskArticle=false&_' % (channelId,size)
try:
    content_json=requests.get(cmoney_content_url)
    print("成功獲取")
except Exception as err:
    print("獲取失敗")


countrer=0
data=json.loads(content_json.text)
for i in range(size):
    cmoney_content_time=data[i]['ArtCteTm'].replace("/","-")
    cmoney_content_time_final=datetime.strptime(cmoney_content_time,'%Y-%m-%d %H:%M')#發文時間(將字串格式化成時間)
    yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)#抓取範圍為昨天凌成00:00以後
    if cmoney_content_time_final>yesterday:
        countrer+=1
        cmoney_content=data[i]['ArtCtn']
        txt_soup=bs4.BeautifulSoup(cmoney_content,'lxml')
        cmoney_content_txt=txt_soup.find('div','main-content').text #發文內容
        print("第%s篇" % (countrer))
        print(cmoney_content_txt)
        print(cmoney_content_time_final)
        print("-"*50+"分隔線"+"-"*50)

browser.close()
    
        







