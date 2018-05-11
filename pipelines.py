# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline  # 调用下载图片的模块
import pymysql
from pymysql import cursors
from twisted.enterprise import adbapi
class MySQLTwistedPipline(object):
    # 异步读取MySQL
    @classmethod
    def from_settings(cls,settings):
        dbparms=dict(
        host=settings["MYSQL_HOST"],
        db=settings["MYSQL_DBNAME"],
        user=settings["MYSQL_USER"],
        passwd=settings["MYSQL_PASSWORD"],
        charset='utf8',
        cursorclass=cursors.Cursor,
        use_unicode=True
        )
        dbpool=adbapi.ConnectionPool("pymysql",**dbparms)
        return cls(dbpool)
    def __init__(self,dbpool):
        self.dbpool=dbpool
    def process_item(self,item,spider):
        # 使用twised将mysql插入变成异步调用
        query=self.dbpool.runInteraction(self.insert_item,item)
        # query.addErrback(self.handler_error,item,spider)  # 处理异常
        return item
    def handler_error(self,failure,item,spider):
        # 处理异步插入异常
        print(failure)
    def insert_item(self,cursor,item):
        # 执行具体的插入
        sql="""
            INSERT INTO douban_spider1(title,author,time,date,weekday,article_url,author_url,topics,recomment_num) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)ON DUPLICATE KEY UPDATE time=VALUES(time),recomment_num=VALUES(recomment_num),date=VALUES (date),weekday=VALUES (weekday)
            """  # 怎么更新Mysql通过python语句
        cursor.execute(sql,(item['title'],item['author'],item['time'],item['date'],item['weekday'],item['article_url'],item['author_url'],item['topics'],item['recomment_num']))
