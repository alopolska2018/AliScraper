# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AliItem(scrapy.Item):
    # define the fields for your item here like:
    products = scrapy.Field()
    desc_url = scrapy.Field()
