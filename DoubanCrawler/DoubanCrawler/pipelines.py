# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql
import pymongo
from pymongo import MongoClient


class BookPipeline(object):
    def open_spider(self, spider):
        self.db = pymysql.connect(host="localhost", user="root", password="123456", db="douban", use_unicode=True,
                                  charset="utf8")
        self.cur = self.db.cursor()

    def process_item(self, item, spider):
        if spider.name != "book_spider":
            return item
        sql_insert = "insert into book_250(url,title,author,rating_num,rating_people) values('{}','{}','{}',{},{}) ".format(
            item['url'], item['title'], item['author'], item['rating_num'], item['rating_people']
        )
        self.cur.execute(sql_insert)
        self.db.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.db.close()


class UserPipeline(object):
    def open_spider(self, spider):
        self.conn = MongoClient('127.0.0.1', 27017)
        self.db = self.conn.douban
        self.user_info = self.db.user_info

    def process_item(self, item, spider):
        if spider.name != "user_spider":
            return item
        self.user_info.insert({"_id": item['uid'], "name": item['name'], "sign": item['sign'],
                               "addr": item['addr'], "reg_time": item['reg_time'],
                               "follows": item['follows'], "fans": item['followers'], "intro": item['intro']})
        return item

    def close_spider(self, spider):
        self.conn.close()
