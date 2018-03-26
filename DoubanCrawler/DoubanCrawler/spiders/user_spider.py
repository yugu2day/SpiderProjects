# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from ..items import UserItem
import re


class UserSpiderSpider(CrawlSpider):
    name = 'user_spider'
    allowed_domains = ['www.douban.com']
    start_urls = ['https://www.douban.com/people/3703176/']

    rules = (
        Rule(LinkExtractor(allow=r'/people/.*?/', deny=r'/account'), callback='parse_item', follow=False),
    )

    def parse_item(self, response):

        i = UserItem(followers=0, follows=0, intro='', sign='')
        i['uid'] = response.xpath("//div[@class='user-info']/div/text()").extract()[0].strip()
        i['name'] = response.xpath("//div[@class='info']/h1/text()").extract_first().strip()
        i['sign'] = response.xpath("//div[@class='info']/h1/div/text()").extract_first().strip()
        i['addr'] = response.xpath("//div[@class='user-info']/a/text()").extract_first().strip()
        i['reg_time'] = response.xpath("//div[@class='user-info']/div/text()").extract()[1][:-2].strip()
        i['intro'] = response.xpath("//div[@class='user-intro']//span").extract()[0]  # 返回span标签下所有内容
        i['follows'] = response.xpath("//div[@id='friend']//span[@class='pl']/a/text()").extract_first()[2:]
        follower_str = response.xpath("//p[@class='rev-link']/a/text()").extract_first()
        i['followers'] = re.search('被([0-9]*)', follower_str).groups()[0]
        yield i
        # 获取可见的关注者
        obus = response.xpath("//div[@id='friend']//a/@href").extract()
        for obu in obus:
            yield scrapy.Request(obu, callback='parse_item')