# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from pymongo import MongoClient
from bson.objectid import ObjectId

class AliPipeline(object):

    def __init__(self):
        self.client = MongoClient()
        self.client = MongoClient('localhost', 27017)
        db = self.client['ali']
        self.collection = db['ali_tb']

    def process_item(self, item, spider):
        a = self.collection.find_one_and_update({"product_id": item['product_id']},
                                                {"$set": { "woocommerce_id": 0,
                                                           "data": item }
                                                 }, upsert=True)
        # print('Product id: {}. Added to db as: {}'.format(item['product_id']), ObjectId(a['_id']))
        return item
