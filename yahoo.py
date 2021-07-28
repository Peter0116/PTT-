import requests
import json
import bs4
from datetime import datetime, timedelta
import sys

stock=input("輸入要找的股票公司")
page=1
count=0

def find_stock_news():
    global count
    for i in find_title:
        find_title_url=i.find('a').get('href')
        if find_title_url.startswith("/news/"):
            news_url='https://tw.stock.yahoo.com/'+find_title_url  #新聞文章網址
            try:
                news_url_html=requests.get(news_url)
                news_url_soup=bs4.BeautifulSoup(news_url_html.text,'lxml')
                news_url_title=news_url_soup.find("header","caas-title-wrapper").find('h1').text
                news_url_content=news_url_soup.find("div","caas-content-wrapper").find('div','caas-body').find_all('p')
                news_date=news_url_soup.find("time").text
                news_date=news_date.replace("上午","")
                news_date=news_date.replace("下午","")
                news_date=datetime.strptime(news_date,'%Y年%m月%d日 %H:%M')
                yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)
            except Exception as err:
                print(err)
            if news_date>yesterday:
                count+=1
                print('第%s篇' % count)
                print("發文時間:"+str(news_date))
                print("文章連結:"+news_url)
                print("文章標題:"+news_url_title)
                print("文章內容:")
                for i in news_url_content:
                    print(i.text)
                print("-"*50+"分隔線"+"-"*50)
            else:
                break
fn='stock_code_name.json' #請先下載 stock_code_name.json 檔案 並修改fn路徑
with open (fn,'r',encoding="utf-8") as fnobj:
    datas=json.load(fnobj)
for data in datas:
    if data[1]==stock:
        stock=(data[0]) #將股票公司名子轉換成股票公司代碼


for i in range(20):
    url='https://tw.stock.yahoo.com/q/h?s=%s&pg=%s' % (stock,page)
    stock_html=requests.get(url)
    stock_soup=bs4.BeautifulSoup(stock_html.text,'lxml')
    find_title=stock_soup.find_all('td',valign="bottom")
    find_stock_news()
    page+=1



sys.exit("抓取結束,無資料代表兩天內無相關新聞")   


