# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os

import requests

ROOT_DIR = "E://妹子图/"
headers = {
    'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    'upgrade-insecure-requests': "1",
    'user-agent': "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.119 Safari/537.36",
    }
proxies = {"http//": "114.230.41.94:3128"}


class MzScrapyPipeline(object):
    def process_item(self, item, spider):
        dir_path = '{}/{}/{}/'.format(ROOT_DIR, item['tag'], item['title'])
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        file_name = item['image_urls'][-7:]
        file_path = dir_path + file_name
        with open(file_path, 'wb') as handle:
            headers['referer'] = item['url']
            response = requests.get(item['image_urls'], headers=headers, proxies=proxies)
            handle.write(response.content)
        return item
