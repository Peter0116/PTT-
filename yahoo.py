import requests
import json
import bs4
from datetime import datetime, timedelta
import sys
from html.parser import HTMLParser
import pandas as pd
import sqlite3

class HTMLCleaner(HTMLParser):#清洗文章數據,只要有html標籤就清除
    def __init__(self, *args, **kwargs):
        super(HTMLCleaner, self).__init__(*args, **kwargs)
        self.data_list = []

    def handle_data(self, data):
        self.data_list.append(data)
cleaner = HTMLCleaner()

page=0
count=0
stock=input("輸入要找的股票公司")

fn='stock_code_name.json' #請先下載 stock_code_name.json 檔案 並修改fn路徑
with open (fn,'r',encoding="utf-8") as fnobj:
    datas=json.load(fnobj)
for data in datas:
    if data[1]==stock:
        stock=(data[0]) #將股票公司名子轉換成股票公司代碼

connect = sqlite3.connect('News.db')
cursor = connect.cursor()
df= pd.DataFrame(columns= ["date","hour","ticker","url","title","content"])

for i in range(20):
    page+=1
    url='https://tw.stock.yahoo.com/q/h?s=%s&pg=%s' % (stock,page)
    stock_html=requests.get(url)
    stock_soup=bs4.BeautifulSoup(stock_html.text,'lxml')
    find_title=stock_soup.find_all('td',valign="bottom")
    for i in find_title:
        find_title_url=i.find('a').get('href')
        if find_title_url.startswith("/news/"):
            news_url='https://tw.stock.yahoo.com/'+find_title_url  #新聞文章網址
            try:
                news_url_html=requests.get(news_url)
                news_url_soup=bs4.BeautifulSoup(news_url_html.text,'lxml')
                news_title=news_url_soup.find("header","caas-title-wrapper").find('h1').text
                news_url_content=news_url_soup.find("div","caas-content-wrapper").find('div','caas-body').find_all('p')
                news_date=news_url_soup.find("time").text
                news_date=news_date.replace("上午","AM").replace("下午","PM").replace("週日","Sun").replace("週一","Mon").replace("週二","Tue").replace("週三","Wed").replace("週四","Thur").replace("週五","Fri").replace("週六","Sat")
                news_date=datetime.strptime(news_date,'%Y年%m月%d日 %p%H:%M')
                today=datetime.now().replace(hour=0,minute=0,second=0)
                # yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)
            except Exception as err:
                print(err)
            if news_date>today:
                count+=1
                content=[]
                for i in news_url_content:
                    content.append(i)
                content="".join('%s' %id for id in content).replace("\n",'').replace("\\n",'').replace("\xa0",'').replace("\t","").replace('\"','').replace("\'","").replace("\x20",'').replace(",,'","").replace("\'","").replace("\',","")
                cleaner.feed(content)
                content=cleaner.data_list #清洗過後的文章內容
                payload = [*(str(news_date).split()), stock, news_url, news_title, str(content)]
                df.loc[len(df)] = payload
                print('第%s篇' % count)
                print("發文時間:"+str(news_date))
                print("文章連結:"+news_url)
                print("文章標題:"+news_title)
                print("文章內容:"+str(content))
                print("-"*50+"分隔線"+"-"*50)
            else:
                break


df.to_sql(f'yahoo', connect, if_exists='append', index=False)
connect.commit()
sys.exit("抓取結束,無資料代表今天無相關新聞")   
