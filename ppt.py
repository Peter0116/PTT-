import requests
import bs4
from datetime import datetime, timedelta
import sys
import sqlite3
import pandas as pd
import json
from html.parser import HTMLParser

class HTMLCleaner(HTMLParser):#清洗文章數據,只要有html標籤就清除
    def __init__(self, *args, **kwargs):
        super(HTMLCleaner, self).__init__(*args, **kwargs)
        self.data_list = []

    def handle_data(self, data):
        self.data_list.append(data)
cleaner = HTMLCleaner()

page=0
count=0
stock=input("輸入要找的公司股票完整名字")
url='https://www.ptt.cc/bbs/Stock/search?page=%s&q=%s' % (page,stock)

fn='stock_code_name.json' #請先下載 stock_code_name.json 檔案 並修改fn路徑
with open (fn,'r',encoding="utf-8") as fnobj:
    datas=json.load(fnobj)
for data in datas:
    if data[1]==stock:
        stock_ticker=(data[0]) #將股票公司名子轉換成股票公司代碼

connect = sqlite3.connect('News.db')
cursor = connect.cursor()
df= pd.DataFrame(columns= ["date","hour","ticker","url","title","content"])

for i in range(10):
    page+=1
    url='https://www.ptt.cc/bbs/Stock/search?page=%s&q=%s' % (page,stock)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    ppt_html=requests.get(url,headers=headers)
    ppt_soup=bs4.BeautifulSoup(ppt_html.text,'lxml')
    ppt_article=ppt_soup.find_all('div','r-ent')
    for i in ppt_article:
        article_url='https://www.ptt.cc/'+i.find('a').get('href') #文章連結
        article_title=i.find('a').text                            #文章標題
        article_html=requests.get(article_url,headers=headers)
        article_soup=bs4.BeautifulSoup(article_html.text,"lxml")
        article_date=article_soup.find_all('span','article-meta-value')[3].text #發文時間
        article_date=datetime.strptime(article_date,'%a %b %d %H:%M:%S %Y') #格式化時間
        today=datetime.now().replace(hour=0,minute=0,second=0)
        # yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)
        if article_date>today:
            count+=1
            article_content=article_soup.find('div',id="main-content")
            article_push=article_soup.find("div","push")
            article_push_index=list(article_content).index(article_push)
            content=str((list(article_content)[4:article_push_index-2])).replace("\n",'').replace("\\n",'').replace("\xa0",'').replace("\t","").replace('\"','').replace("\'","").replace("\x20",'').replace(",,'","").replace("\'","")
            cleaner.feed(content)
            content=cleaner.data_list #清洗過後的文章內容
            payload = [*(str(article_date).split()), stock_ticker, article_url, article_title, str(content)]
            df.loc[len(df)] = payload
            print("第%s篇:" % (count))
            print("發文時間:"+str(article_date))
            print("文章連結:"+article_url)
            print("標題:"+article_title)
            print("文章內容:"+str(content))
            print("-"*50+"分隔線"+"-"*50)
        else:
            break
        

df.to_sql(f'ptt', connect, if_exists='append', index=False)
connect.commit()
sys.exit("抓取結束,無資料代表今天無相關新聞") 
    
