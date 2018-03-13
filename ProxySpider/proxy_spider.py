# -*-coding:utf-8-*-
# !/usr/bin/env python
"""
地址：http://www.xicidaili.com/nt/
将可用IP地址保存到csv文件中
"""
import csv
from random import randint
from multiprocessing import Pool

import requests
import lxml.html
import time
from urllib3.exceptions import ReadTimeoutError

TARGET_URL = "http://www.xicidaili.com/nt/"
FILE_NAME = r"proxy_ip.csv"

headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'accept-encoding': "gzip, deflate",
    'accept-language': "zh-CN,zh;q=0.9",
    'cache-control': "no-cache",
    'connection': "keep-alive",
    'cookie': "_free_proxy_session=BAh7B0kiD3Nlc3Npb25faWQGOgZFVEkiJWVjMzYzZGJmZGIxMzUxYTAzNjUxZWNmNmNkNjE4ODZiBjsAVEkiEF9jc3JmX3Rva2VuBjsARkkiMVJVQTV5V1NudEhjM3M2d0g0NGQ3UlhwZnNRVzdhckR4YkhyaVMzaFJsV2s9BjsARg%3D%3D--5e5324b747a06deaca4d4b1636192c49e9afc42d; Hm_lvt_0cf76c77469e965d2957f0553e6ecf59=1519635706; Hm_lpvt_0cf76c77469e965d2957f0553e6ecf59=1519637646",
    'host': "www.xicidaili.com",
    'if-none-match': "W/\"61f3e567b1a5028acee7804fa878a5ba\"",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
    'postman-token': "c290f8f7-894e-5983-a736-b23bf0c7943d"
}


def getProxyList(target_url=TARGET_URL, pages='1'):
    """
    爬取代理IP地址
    :param target_url: 爬取的代理IP网址
    :return:
    """
    proxyFile = open(FILE_NAME, "a+", newline="")
    writer = csv.writer(proxyFile)

    r = requests.get(target_url + pages, headers=headers, timeout=2.5)
    document_tree = lxml.html.fromstring(r.text)
    rows = document_tree.cssselect("#ip_list tr")
    rows.pop(0)
    for row in rows:
        tds = row.cssselect("td")
        proxy_ip = tds[1].text_content()
        proxy_port = tds[2].text_content()
        proxy_addr = tds[3].text_content().strip()
        proxy_type = tds[5].text_content()
        writer.writerow([proxy_type, proxy_ip, proxy_port, proxy_addr])

    proxyFile.close()


def verifyProxy(verify_url, proxies):
    headers = {
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
    }
    try:
        r = requests.get(verify_url, headers=headers, proxies=proxies, timeout=10.0)
        if r.status_code == 200:
            print(str(proxies) + " verified")
        else:
            print(str(proxies) + " failed" + r.status_code)
    except:
        print(str(proxies) + " failed")

def verifyProxies(verify_url="http://www.baidu.com", file_path=FILE_NAME):
    proxyFile = open(FILE_NAME, "r+")
    csv_reader = csv.reader(proxyFile)
    p = Pool(10)
    for row in csv_reader:
        if row[0] == 'HTTP':
            proxies = {"http": "http://" + row[1] + ":" + row[2]}
        elif row[0] == 'HTTPS':
            proxies = {"https": "https://" + row[1] + ":" + row[2]}
        p.apply_async(verifyProxy, args=(verify_url, proxies))
        time.sleep(randint(1, 3))
    p.close()
    p.join()
    proxyFile.close()


if __name__ == "__main__":
    # for i in range(5, 10):
    #     getProxyList(pages=str(i))
    verifyProxies()
#