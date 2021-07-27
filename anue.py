from datetime import datetime, timedelta
import json
import requests
import bs4
import sys


stock=input("輸入要找的股票公司")
url='https://ess.api.cnyes.com/ess/api/v1/news/keyword?q=%s&limit=1000&page=1' % (stock)   #一次抓取1000筆新聞  

headers = {'user-agent': 'Mozilla/5.0 (Macintosh Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36'}

try:
    stock_json=requests.get(url,headers=headers)
    print("成功獲取json檔案")
except Exception as err:
    print("獲取失敗原因:",err)

count=0
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
    yesterday=(datetime.now()+timedelta(-1)).replace(hour=0,minute=0,second=0)
    new_content=news_soup.find_all('div','_2E8y')
    if news_date>yesterday:
        count+=1
        print("第%s篇:" % (count))
        print("發文時間:"+str(news_date))
        print("文章連結:"+news_url)
        print("標題:"+news_title)
        print("文章內容:")
        for i in new_content:
            content=i.find_all("p")
            for j in content:
                print(j.text)
        print("-"*50+"分隔線"+"-"*50)
    else:
        break

sys.exit("抓取結束")
