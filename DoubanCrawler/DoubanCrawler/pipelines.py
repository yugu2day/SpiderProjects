# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql


class BookPipeline(object):

    def open_spider(self, spider):
        self.db = pymysql.connect(host="localhost", user="root", password="123456", db="douban", use_unicode=True,
                                  charset="utf8")
        self.cur = self.db.cursor()

    def process_item(self, item, spider):
        sql_insert = "insert into book_250(url,title,author,rating_num,rating_people) values('{}','{}','{}',{},{}) ".format(
            item['url'], item['title'], item['author'], item['rating_num'], item['rating_people']
        )
        self.cur.execute(sql_insert)
        self.db.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.db.close()
