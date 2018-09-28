# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from pymongo import *

from joox_search_and_detail.items import *
from joox_search_and_detail.utils import *


class JooxSearchAndDetailPipeline(object):

    def __init__(self):
        self.mongo_dao = MongoDao().get_instance()
        self.mongo_dao['JooxSearchItem'].create_index([("search_input", ASCENDING)], unique=True)
        self.mongo_dao['JooxSongDetailsItem'].create_index([("songid", ASCENDING)], unique=True)

    def process_item(self, item, spider):

        if isinstance(item, JooxSearchItem):
            self.mongo_dao['JooxSearchItem'].replace_one({'search_input': item['search_input']}, dict(item), upsert=True)
        elif isinstance(item, JooxSongDetailsItem):
            self.mongo_dao['JooxSongDetailsItem'].replace_one({'songid': item['songid']}, dict(item), upsert=True)
        else:
            raise KeyError
