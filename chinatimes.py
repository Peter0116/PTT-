import requests
import json
import bs4
from datetime import datetime, timedelta
import sys
from html.parser import HTMLParser
import pandas as pd
import sqlite3

count=0
page=0
stock=input("輸入要找的股票公司")

fn='stock_code_name.json' #請先下載 stock_code_name.json 檔案 並修改fn路徑
with open (fn,'r',encoding="utf-8") as fnobj:
    datas=json.load(fnobj)
for data in datas:
    if data[1]==stock:
        stock_ticker=(data[0]) #將股票公司名子轉換成股票公司代碼

connect = sqlite3.connect('News.db')
cursor = connect.cursor()
df= pd.DataFrame(columns= ["date","hour","ticker","url","title","content"])

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
        today=datetime.now().replace(hour=0,minute=0,second=0)
        # yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)
        if news_date>today:
            count+=1
            news_html=requests.get(news_url)
            news_soup=bs4.BeautifulSoup(news_html.text,'lxml')
            news_content=news_soup.find('div','article-body').find_all('p')
            content=[]
            for i in news_content:
                content.append(i.text)
            content="".join(content).replace("\n",'').replace("\\n",'').replace("\xa0",'').replace("\t","").replace('\"','').replace("\'","").replace("\x20",'').replace(",,'","").replace("\'","").replace("\',","")
            payload = [*(str(news_date).split()), stock_ticker, news_url, news_title, str(content)]
            df.loc[len(df)] = payload
            print("第%s篇:" % (count))
            print("發文時間:"+str(news_date))
            print("文章連結:"+news_url)
            print("標題:"+news_title)
            print("文章內容:"+str(content))
            print("-"*50+"分隔線"+"-"*50)
        else:
            break

df.to_sql(f'chinatimes', connect, if_exists='append', index=False)
connect.commit()

sys.exit("抓取結束,無資料代表今天無相關新聞") 
