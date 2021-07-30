from datetime import datetime, timedelta
from sqlite3.dbapi2 import connect
import bs4
import requests
import json
import pandas as pd
import sqlite3
import sys


stock=input("輸入要找的股票公司")
size=500 #一次讀取500筆資料
dcard_json_url='https://www.dcard.tw/service/api/v2/search/posts?limit=%s&query=%s&forum=stock&highlight=true&country=TW' % (size,stock)

fn='stock_code_name.json' #請先下載 stock_code_name.json 檔案 並修改fn路徑
with open (fn,'r',encoding="utf-8") as fnobj:
    datas=json.load(fnobj)
for data in datas:
    if data[1]==stock:
        stock_ticker=(data[0]) #將股票公司名子轉換成股票公司代碼

connect = sqlite3.connect('News.db')
cursor = connect.cursor()
df= pd.DataFrame(columns= ["date","hour","ticker","url","title","content"])


try:
    dcard_json=requests.get(dcard_json_url)
    print("成功獲取500則發文")
except Exception as err:
    print("獲取失敗")

count=0 #計算評論數量

data=json.loads(dcard_json.text)
for i in data:
    article_title=(i['title'])
    article_url='https://www.dcard.tw/f/stock/p/'+str(i['id'])
    date=str(i['createdAt'])
    article_date=datetime.strptime(date[0:19],'%Y-%m-%dT%H:%M:%S')
    today=datetime.now().replace(hour=0,minute=0,second=0)
    yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)#抓取範圍為昨天00:00以後
    if article_date>yesterday:
        count+=1
        article_html=requests.get(article_url)
        article_soup=bs4.BeautifulSoup(article_html.text,'lxml')       
        content=article_soup.find("div",'sc-1npvbtq-0 gfjrnD').find('div','phqjxq-0 fQNVmg').find('span').text
        content="".join(content).replace("\n",'').replace("\\n",'').replace("\xa0",'').replace("\t","").replace('\"','').replace("\'","").replace("\x20",'').replace(",,'","").replace("\'","").replace("\',","")
        payload = [*(str(article_date).split()), stock_ticker, article_url, article_title, content]
        df.loc[len(df)] = payload
        print("第%s篇" % (count)) #第N篇文章
        print(article_date) #發文時間
        print(article_url) #文章連結
        print(article_title)
        print(content) #評論內容
        print("-"*50+"分隔線"+"-"*50)

df.to_sql(f'dcard', connect, if_exists='append', index=False)
connect.commit()
sys.exit("抓取結束,無資料代表今天無相關文章") 
