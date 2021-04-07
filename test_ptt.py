import requests 
import time
from bs4 import BeautifulSoup
import os
import re
import urllib.request
import json


PTT_URL='https://www.ptt.cc'
#取得網頁文件的function
def get_web_page(url):
    time.sleep(0.5)  #每次爬取暫停0.5秒 以免被判定惡意爬取
    resp = requests.get(
        url=url,
        cookies={'over18':'1'}
)
    if resp.status_code != 200:
        print('Invanlid url:',resp.url)
        return None
    else:
        return resp.text
def get_articles(dom, date):
    soup = BeautifulSoup(dom, 'html.parser')
    #取得上一頁的連結
    paging_div = soup.find('div','btn-group btn-group-paging')
    prev_url = paging_div.find_all('a')[1]['href']
    articles=[]
    divs = soup.find_all('div','r-ent')
    for d in divs:
        if d.find('div','date').string.strip() == date:  #strip() 移除頭尾字符<-通常是空白或是換行符號
            push_count=0
            if d.find('div','nrec').string:
                try:
                    push_count = int(d.find('div','nrec').string)
                except ValueError:
                    pass
            if d.find('a'):
                href = d.find('a')['href']
                title = d.find('a').string
                articles.append({
                    'title':title,
                    'href':href,
                    'push_count':push_count})
    return articles, prev_url

def parse(dom):
    soup = BeautifulSoup(dom,'html.parser')
    links = soup.find(id='main-content').find_all('a')
    img_urls=[]
    for link in links:
        if re.match(r'^https?://(i.)?(m.)?imgur.com',link['href']):
            img_urls.append(link['href'])
    return img_urls

def save(img_urls, title):
    if img_urls:
        try:
            dname = title.strip()  # 用 strip() 去除字串前後的空白
            os.makedirs(dname)
            for img_url in img_urls:
                if img_url.split('//')[1].startswith('m.'):
                    img_url = img_url.replace('//m.', '//i.')
                if not img_url.split('//')[1].startswith('i.'):
                    img_url = img_url.split('//')[0] + '//i.' + img_url.split('//')[1]
                if not img_url.endswith('.jpg'):
                    img_url += '.jpg'
                fname = img_url.split('/')[-1]
                urllib.request.urlretrieve(img_url, os.path.join(dname, fname))
        except Exception as e:
            print(e)
if __name__ == '__main__':
    current_page = get_web_page(PTT_URL+'/bbs/Beauty/index.html')
    if current_page:
        articles=[]
        date = time.strftime('%m/%d').lstrip('o')
        current_articles, prev_url = get_articles(current_page, date)
        while current_articles:
            articles += current_articles
            current_page = get_web_page(PTT_URL+prev_url)
            current_articles, prev_url = get_articles(current_page,date)
        for article in articles:
            print('Processing:', article)
            page = get_web_page(PTT_URL+article['href'])
            if page:
                img_urls = parse(page)
                save(img_urls, article['title'])
                article['num_image']=len(img_urls)
        with open('date.json','w',encoding='utf-8') as f:
            json.dump(articles,f,indent=2,sort_keys=True,ensure_ascii=False)
'''
看板內容需要18歲才可瀏覽  set-cookie : over 18 = 1
所需文章資料
每一篇文章 <div class='r-ent'>
標題 : <a>text
網址 : <a href= >
推文數 : <div class='nrec'>
日期 : <div class='date'>
上頁按鈕所在 : <div class='btn-group btn-group-paging'>
'''

#json.loads()是将str转化成dict格式，json.dumps()是将dict转化成str格式。
#json.load()和json.dump()也是类似的功能，只是与文件操作结合起来了。
#join()： 连接字符串数组。将字符串、元组、列表中的元素以指定的字符(分隔符)连接生成一个新的字符串
#Skipkeys：默认值是False，如果dict的keys内的数据不是python的基本类型(str,unicode,int,long,float,bool,None)，设置为False时，就会报TypeError的错误。此时设置成True，则会跳过这类key
#ensure_ascii：默认值True，如果dict内含有non-ASCII的字符，则会类似\uXXXX的显示数据，设置成False后，就能正常显示
#indent：应该是一个非负的整型，如果是0，或者为空，则一行显示数据，否则会换行且按照indent的数量显示前面的空白，这样打印出来的json数据也叫pretty-printed json
#separators：分隔符，实际上是(item_separator, dict_separator)的一个元组，默认的就是(‘,’,’:’)；这表示dictionary内keys之间用“,”隔开，而KEY和value之间用“：”隔开。
#encoding：默认是UTF-8，设置json数据的编码方式。
#sort_keys：将数据根据keys的值进行排序。(a-z)


