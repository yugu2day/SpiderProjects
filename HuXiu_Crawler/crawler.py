# -*-coding:utf-8-*-
# !/usr/bin/env python
import random
import re

import gevent
import requests
import time
from bs4 import BeautifulSoup
import lxml.html
from pymongo import MongoClient
from gevent import queue
from gevent.pool import Pool
from HuXiu_Crawler.resource import PROXIES, DEFAULT_REQUEST_HEADERS

root_url = 'https://www.huxiu.com'
conn = MongoClient('127.0.0.1', 27017)
g_pool = Pool(10)
g_queue = queue.Queue()


def initMongo():
    '''初始化数据库并返回操作的集合'''
    global conn
    db = conn.huxiu
    news_collection = db.news_collection
    print("数据库已就绪")
    return news_collection


def parse_start_url(url, news_collection):
    '''解析首页获取文章地址'''
    r = requests.get(url, headers=DEFAULT_REQUEST_HEADERS, proxies={"http": random.choice(PROXIES)})
    print(r.status_code)
    urls = get_url(r.text)
    for url in urls:
        g_queue.put_nowait(url['href'])


def parse_page(news_collection):
    url = root_url + g_queue.get_nowait()
    # 判断是否已经浏览过
    if news_collection.find_one({"_id": url.split('/')[-1]}):
        print("已存在")
        return

    '''解析页面并存入数据库'''
    r = requests.get(url, headers=DEFAULT_REQUEST_HEADERS, proxies={"http": random.choice(PROXIES)})
    uid = r.url.split('/')[-1]  # 文章标号
    etree = lxml.html.fromstring(r.text)
    title = etree.xpath("string(//h1[@class='t-h1'])").strip()
    author = etree.xpath("string(//span[@class='author-name']/a)")
    date = etree.xpath("string(//span[contains(@class,'article-time')])")
    shares = etree.xpath("string(//span[contains(@class,'article-share')])")[2:]
    comments = etree.xpath("string(//span[contains(@class,'article-pl')])")[2:]
    tag = etree.xpath("string(//a[@class='column-link'])")
    content = etree.xpath("//div[@class='article-content-wrap']")[0]
    content = lxml.html.tostring(content, method='html', encoding='utf-8')  # 获取标签内所有内容并将结果转化为字符串
    content = str(content, 'utf-8')
    news_collection.insert({"_id": uid, "title": title, "author": author, "date": date,
                            "shares": shares, "comments": comments, "tag": tag, "content": content
                            })
    print("已添加:" + title)
    get_related_urls(uid)

        # print(uid)
        # print(title)
        # print(author)
        # print(date)
        # print(shares)
        # print(comments)
        # print(tag)
        # print(content)


def get_related_urls(uid):
    '''获取当前文章的相关文章id'''
    url = "https://www.huxiu.com/relatedArticle/" + uid
    r = requests.get(url, headers=DEFAULT_REQUEST_HEADERS, proxies={"http": random.choice(PROXIES)})
    str = r.content.decode('unicode_escape')
    # 获取相关新闻id的列表
    data_ids = re.findall("data-id=\"(.*?)\"", str)
    for id in data_ids:
        uid = "/article/" + id + ".html"
        g_queue.put_nowait(uid)


def get_url(html):
    '''通过解析html文档，返回该页面上的新闻链接'''
    soup = BeautifulSoup(html, 'lxml')
    urls = soup.find_all('a', attrs={'href': re.compile('/article/[0-9]+.html')})
    urls = set(urls)
    return urls


if __name__ == "__main__":
    try:
        news_collection = initMongo()
        parse_start_url("https://www.huxiu.com", news_collection)
        while not g_queue.empty():
            g_pool.spawn(parse_page, news_collection)
            g_pool.spawn(parse_page, news_collection)
            g_pool.spawn(parse_page, news_collection)
            g_pool.spawn(parse_page, news_collection)
            g_pool.spawn(parse_page, news_collection)
    except Exception as e:
        print(e)
    finally:
        conn.close()
        g_pool.kill()
