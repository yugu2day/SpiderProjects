#-*-coding:utf-8-*-
#!/usr/bin/env python
import re
from random import randint

import requests
import lxml.html
import gevent
import time
from pymongo import MongoClient

ROOT_URL="http://www.ygdy8.net"
CN_URL = ROOT_URL + r"/html/gndy/china/list_4_{}.html"          #国内电影
OM_URL = ROOT_URL + r"/html/gndy/oumei/list_7_{}.html"          #欧美电影
JP_URL = ROOT_URL + r"/html/gndy/rihan/list_6_{}.html"          #日韩电影
NEW_URL = ROOT_URL + r"/html/gndy/dyzz/list_23_{}.html"        #最新电影

headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,zh;q=0.9",
    'cache-control': "no-cache",
    'connection': "keep-alive",
    'cookie': "37cs_user=37cs73167551783; 37cs_show=69; 37cs_pidx=5; cscpvcouplet4298_fidx=3; cscpvrich5041_fidx=3",
    'host': "www.ygdy8.net",
    'if-modified-since': "Wed, 21 Feb 2018 095206 GMT",
    'if-none-match': "\"027aea1f9aad3158c\"",
    'referer': "http//www.ygdy8.net/html/gndy/index.html",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
    'postman-token': "d4374eb4-d54d-f083-973f-b0d4db809f56"
}

'''初始化MongoDB，数据库为movieDB，COLLECTION_NAME为movie'''
conn = MongoClient('127.0.0.1', 27017)
db = conn.movieDB
movie = db.movie
session = requests.session()

def getPages(html):
    '''
    通过传入的html代码解析获取主页下的页面数
    '''
    total_pages = re.findall("共(.*?)页",html)
    return int(total_pages[0])

def parseLink(urls):
    '''
    解析电影界面的数据并存储
    '''
    for url in urls:
        if movie.find_one({"_id":url}):
            print("已存在")
            continue
        response = session.request("GET", url, headers=headers)
        response.encoding = "gb2312"
        tree = lxml.html.fromstring(response.text)
        url = response.url
        title = tree.xpath("//div[@class='title_all']//font")[0].text_content()
        print(url)
        download = re.findall("(ftp:.*?(\.rmvb|\.mkv|\.mp4))", response.text)
        rank = re.findall(r"评分 ([0-9].*?)/",response.text)
        if len(rank)==0:
            rank=""
        else:
            rank = float(rank[0])
        movie.insert({"_id":url,"title":title,"download":download[0][0],"rank":rank})
        print("已添加电影"+title)


def getLinks(url):
    urls = []
    response = session.request("GET", url, headers=headers)
    tree = lxml.html.fromstring(response.text)
    links = tree.xpath("//div[@class='co_content8']//a[@class='ulink']")
    for link in links:
        if not link.get('href').endswith("index.html"):
            urls.append(ROOT_URL+link.get('href'))
    parseLink(urls)
    time.sleep(randint(0,5))
    return urls

def getMovie(url):
    response = session.request("GET", url.format('1'), headers=headers)
    response.encoding = 'gb2312'
    total_pages = getPages(response.text)
    greenlets = []
    for i in range(1, total_pages + 1):
        # greenlets.append(gevent.spawn(getLinks,CN_URL.format(str(i))))
        greenlets.append(gevent.spawn(getLinks, url.format(str(i))))

    gevent.joinall(greenlets=greenlets)


if __name__ == "__main__":
    getMovie(JP_URL)
    getMovie(CN_URL)
    getMovie(OM_URL)
    getMovie(NEW_URL)
    conn.close()