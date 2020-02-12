# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient

class AliPipeline(object):

    def __init__(self):
        self.client = MongoClient()
        self.client = MongoClient('localhost', 27017)
        db = self.client['ali']
        self.collection = db['ali_tb']

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item
