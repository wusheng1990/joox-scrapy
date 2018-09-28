# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class JooxSearchAndDetailItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class JooxSearchItem(scrapy.Item):

    singer_names = scrapy.Field()
    song_name = scrapy.Field()
    search_input = scrapy.Field()
    resp = scrapy.Field()
    status = scrapy.Field()

class JooxSongDetailsItem(scrapy.Item):

    songid = scrapy.Field()
    m4aUrlAliOss = scrapy.Field()
    resp = scrapy.Field()
    status = scrapy.Field()