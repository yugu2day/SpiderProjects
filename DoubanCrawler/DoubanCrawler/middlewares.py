# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html
import random

from scrapy import signals
from .resource import USER_AGENT_LIST, PROXIES


class ProxyMiddleware(object):
    '''设置代理IP'''

    def process_request(self, request, spider):
        pro_adr = random.choice(PROXIES)
        print("USE PROXY -> " + pro_adr)
        request.meta["proxy"] = "http://" + pro_adr.strip()


class RandomUserAgentMiddleware(object):
    '''设置请求头'''

    def process_request(self, request, spider):
        ua = random.choice(USER_AGENT_LIST)
        if ua:
            request.headers.setdefault('User-Agent', ua)



