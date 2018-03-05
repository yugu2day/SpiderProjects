# -*-coding:utf-8-*-
# !/usr/bin/env python

import requests

headers = {
    'Upgrade-Insecure-Requests': '1',
    'Referer': 'http://www.mzitu.com/all/',
    'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
    }
proxies = {"http//": "114.230.41.94:3128"}

with open("01.png", "wb") as f:
    r = requests.get("http://i.meizitu.net/2018/03/03a08.jpg", headers=headers)
    print(r.content)
    f.write(r.content)
