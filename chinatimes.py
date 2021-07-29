from datetime import datetime, timedelta
import requests
import bs4
import sys
import sqlite3
import pandas as pd


count=0
stock=input("輸入要找的股票公司")
page=0

connect = sqlite3.connect('News.db')
cursor = connect.cursor()
df= pd.DataFrame(columns= ["date","hour", "ticker","url","title","content"])

for i in range(20): #抓取20頁 每頁20筆新聞
    page+=1
    url='https://www.chinatimes.com/search/%s?page=%s&chdtv' % (stock,page)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    chinatimes_html=requests.get(url,headers=headers)
    chinatimes_soup=bs4.BeautifulSoup(chinatimes_html.text,'lxml')
    chinatimes_news_url=chinatimes_soup.find('ul','vertical-list list-style-none').find_all('li')

    for i in chinatimes_news_url:
        news_title=i.find('h3','title').find("a").text
        news_url=i.find('h3','title').find("a").get('href')
        date=i.find("time").get("datetime")
        news_date=datetime.strptime(date,'%Y-%m-%d %H:%M')
        yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)
        if news_date>yesterday:
            count+=1
            print("第%s篇:" % (count))
            print("發文時間:"+str(news_date))
            print("文章連結:"+news_url)
            print("標題:"+news_title)
            print("文章內容:")
            news_html=requests.get(news_url)
            news_soup=bs4.BeautifulSoup(news_html.text,'lxml')
            news_content=news_soup.find('div','article-body').find_all('p')
            content = "".join([i.text.replace(u'\xa0', u' ') for i in news_content])
            payload = [*(str(news_date).split()), stock, news_url, news_title, content]
            df.loc[len(df)] = payload
            print("-"*50+"分隔線"+"-"*50)
        else:
            break

df.to_sql(f'chinatime', connect, if_exists='append', index=False)
connect.commit()

sys.exit("抓取結束,無資料代表兩天內無相關新聞")
