# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from ..items import BookItem


class BookSpiderSpider(CrawlSpider):
    name = 'book_spider'
    allowed_domains = ['book.douban.com']
    start_urls = ['https://book.douban.com/top250?icn=index-book250-all']

    rules = (
        Rule(LinkExtractor(allow=r'/subject/'), callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        '''
        解析起始页面
        :param response:
        :return:
        '''
        item_urls = response.xpath("//div[@class='indent']//tr[@class='item']//a//@href").extract()
        for item_url in item_urls:
            yield scrapy.Request(item_url, callback=self.parse_item)
        if (response.xpath("//span[@class='next']/link/@href") == []):
            self.close()
        next_page = response.xpath("//span[@class='next']/link/@href")[0].extract()
        yield scrapy.Request(next_page, callback=self.parse_start_url)

    def parse_item(self, response):
        '''
        解析每个单页
        :param response:
        :return:
        '''
        item = BookItem()
        item['url'] = response.url
        item['title'] = response.xpath("//div[@id='wrapper']/h1/span/text()")[0].extract()
        author = response.xpath("//div[@id='info']//a/text()")[0].extract()
        item['author'] = ''.join(author.split())
        rating_num = response.xpath(r"//strong[@class='ll rating_num ']/text()")[0].extract()
        item['rating_num'] = float(rating_num)
        rating_people = response.xpath(r"//div[@class='rating_sum']/span/a/span/text()")[0].extract()
        item['rating_people'] = int(rating_people)
        return item

