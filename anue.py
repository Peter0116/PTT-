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

count=0
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


url='https://ess.api.cnyes.com/ess/api/v1/news/keyword?q=%s&limit=1000&page=1' % (stock)   #一次抓取1000筆新聞  
headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}

try:
    stock_json=requests.get(url,headers=headers)
    print("成功獲取json檔案")
except Exception as err:
    print("獲取失敗原因:",err)


data=json.loads(stock_json.text)
for i in range(1000):
    news_ID=data['data']['items'][i]['newsId']
    news_title=data['data']['items'][i]['title']
    news_url='https://news.cnyes.com/news/id/%s' % (news_ID)
    headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}
    news_html=requests.get(news_url,headers=headers)
    news_soup=bs4.BeautifulSoup(news_html.text,'lxml')
    news_date=news_soup.find('div','_1R6L').find('time').text
    news_date=datetime.strptime(news_date,'%Y/%m/%d %H:%M')
    # yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)
    today=datetime.now().replace(hour=0,minute=0,second=0)
    new_content=news_soup.find_all('div','_2E8y')
    if news_date>today:
        count+=1
        content=[]
        for i in new_content:
            content_=i.find_all("p")
            for j in content_:
                content.append(j.text)
        content="".join('%s' %id for id in content).replace("\n",'').replace("\\n",'').replace("\xa0",'').replace("\t","").replace('\"','').replace("\'","").replace("\x20",'').replace(",,'","").replace("\'","").replace("\',","")
        cleaner.feed(content)
        content=cleaner.data_list #清洗過後的文章內容
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

df.to_sql(f'anue', connect, if_exists='append', index=False)
connect.commit()
sys.exit("抓取結束,無資料代表今天無相關新聞") 
