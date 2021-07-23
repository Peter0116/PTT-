import time
import requests
import bs4
from datetime import datetime
import re

def find_article_content(article_url):#進入文章連結後，只留下連結內的主要內文
    article_url=article_url
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    ppthtml=requests.get(article_url,cookies={'over18':'1'},headers=headers)
    objsoup=bs4.BeautifulSoup(ppthtml.text,'lxml')
    ppt_context=objsoup.find('div',id="main-content")
    ppt_push=objsoup.find("div","push")
    p=list(ppt_context).index(ppt_push)
    return str((list(ppt_context)[4:p-2]))


def find_sock_article(index): #找尋股票公司(只搜尋今天與昨天的文章,印出標題/網址/內文)
    url=r'https://www.ptt.cc/bbs/Stock/index%d.html' % index
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    ppthtml=requests.get(url,cookies={'over18':'1'},headers=headers)
    objsoup=bs4.BeautifulSoup(ppthtml.text,'lxml')
    pttdiv=objsoup.find_all('div',"r-ent")
    today=[datetime.now().month,datetime.now().day]
    yesterday=[datetime.now().month,datetime.now().day-1]
    for i in pttdiv:
        if i.find('a'):
            date=i.find('div','date').text.split("/")
            date=list(map(int,date))
            if date == today or date==yesterday:
                title=i.find('a').text
                if stock in title:
                    article_url='https://www.ptt.cc'+i.find('a')['href']
                    print("標題:"+i.find('a').text)
                    print("網址:https://www.ptt.cc"+i.find('a')['href'])
                    print("內文:"+find_article_content(article_url))
                    print("-"*50+"分隔線"+"-"*50)

def last_page(url):   #找尋回上一頁連結的網址
    url=url
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    ppthtml=requests.get(url,cookies={'over18':'1'},headers=headers)
    objsoup=bs4.BeautifulSoup(ppthtml.text,'lxml')
    div_page=objsoup.find('div','btn-group btn-group-paging')
    last_page=div_page.find_all('a')[1]['href']
    num=re.search(r'\d{2,6}',last_page)
    return num.group()


stock=input("輸入要找的股票公司")
url='https://www.ptt.cc/bbs/Stock/index.html'

start=int(last_page(url))
number=20
end=start-number
for index in range(start+1,end,-1):
    find_sock_article(index)







