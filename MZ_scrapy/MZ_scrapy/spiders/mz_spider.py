# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from ..items import MzScrapyItem


class MzSpiderSpider(CrawlSpider):
    name = 'mz_spider'
    allowed_domains = ['www.mzitu.com']
    start_urls = ['http://www.mzitu.com/all/']

    rules = (
        Rule(LinkExtractor(allow='/[0-9]+'), callback='parse_item', follow=True),
    )

    def parse_start_url(self, response):
        urls = response.xpath("//ul[@class='archives']//a//@href").extract()
        for url in urls:
            request = scrapy.Request(url, callback=self.parse_item)
            yield request

    def parse_item(self, response):
        i = MzScrapyItem()
        urls = response.xpath("//div[@class='pagenavi']//a/@href").extract()
        # for url in urls:
        #     request = scrapy.Request(url, callback=self.parse_item)
        #     yield request
        i['url'] = response.url
        i['image_urls'] = response.xpath("//div[@class='main-image']//img/@src").extract()[0]
        i['tag'] = response.xpath("//div[@class='main-meta']//a/text()").extract()[0]
        i['title'] = response.xpath("//div[@class='content']/h2/text()").extract()[0].split("（")[0]
        return i
