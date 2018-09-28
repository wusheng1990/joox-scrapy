# -*- coding: utf-8 -*-
import base64
import json
import logging
import urllib.parse
import urllib.request
import codecs
from urllib.parse import quote_plus

from scrapy.http import Request
from scrapy.spiders import CSVFeedSpider
from scrapy.utils.log import configure_logging
from configparser import ConfigParser
from joox_search_and_detail.items import *
from joox_search_and_detail.utils import MongoDao, OssDao
from datetime import datetime
import time
import random

configure_logging(install_root_handler=False)
logging.basicConfig(
    filename='info.log',
    format='%(asctime)s	%(levelname)s: %(message)s',
    level=logging.INFO
)


class MainSpiderSpider(CSVFeedSpider):
    name = 'main_spider'
    allowed_domains = ['api-jooxtt.sanook.com']

    config = ConfigParser()
    config.read('joox_search_and_detail/configs/config.ini')

    start_urls = [config['target']['csvFile']]

    mongo_dao = MongoDao().get_instance()
    oss_prefix = OssDao().get_url_prefix()
    oss_dao = OssDao().get_instance()

    def parse_song_detail_from_joox(self, response):

        resp_str = response.text

        resp_json = json.loads(resp_str)
        ori_song_url = resp_json['m4aUrl']

        extension = '.m4a' if '.m4a' in ori_song_url else '.mp3'
        songid = response.meta['songid']
        search_input = response.meta['search_input']

        try:

            filename = str(int(time.time())) + str(random.randint(1000, 9999)) + extension
            object_name = 'spiders/joox/%s' % filename

            input = urllib.request.urlopen(ori_song_url).read()
            self.oss_dao.put_object(object_name, input)

            yield JooxSongDetailsItem(songid=songid,
                                      m4aUrlAliOss=self.oss_prefix + object_name,
                                      resp=resp_str)
            self.logger.info(
                '[cmd=parse_song_detail_from_joox,msg=success,songid=%s,search_input=%s]' % (songid, search_input))
        except:
            self.logger.exception(
                '[cmd=parse_song_detail_from_joox,msg=fail,songid=%s,search_input=%s]' % (songid, search_input))

    def parse_search_from_joox(self, response):

        resp_str = response.text
        resp_json = json.loads(resp_str)

        search_input = response.meta['search_input']
        singer_names = response.meta['singer_names']
        song_name = response.meta['song_name']

        len_of_itemlist = len(resp_json['itemlist'])
        has_result = len_of_itemlist > 0

        self.logger.info(
            '[cmd=parse_search_from_joox,search_input=%s,len_of_itemlist=%s]' % (search_input, len_of_itemlist))

        if has_result:

            for item in resp_json['itemlist']:

                if 'info1' in item:
                    item['info1_decoded'] = base64.b64decode(item['info1']).decode('utf-8')

                if 'info2' in item:
                    item['info2_decoded'] = base64.b64decode(item['info2']).decode('utf-8')

                if 'info3' in item:
                    item['info3_decoded'] = base64.b64decode(item['info3']).decode('utf-8')

                if 'singer_list' in item:
                    for singer in item['singer_list']:
                        singer['name_decoded'] = base64.b64decode(singer['name']).decode('utf-8')

                songid = item['songid']

                if self.has_joox_song_detail_resp(songid):
                    continue

                url = "http://api-jooxtt.sanook.com/web-fcgi-bin/web_get_songinfo?country=id&lang=en&songid=%s" % songid
                yield Request(
                    url=url,
                    callback=self.parse_song_detail_from_joox,
                    priority=100,
                    meta={'songid': songid, 'search_input': search_input}
                )

        yield JooxSearchItem(singer_names=singer_names, song_name=song_name, search_input=search_input,
                             resp=json.dumps(resp_json), status='Done')

    def parse_row(self, response, row):

        acp_id = row['伴奏id']
        song_name = row['清洗后歌曲名']
        singer_names = row['清洗后歌手名']
        search_input = singer_names + ' ' + song_name

        if self.has_joox_search_resp(search_input):
            return

        self.mongo_dao['JooxSearchItem'].insert_one(
            dict(JooxSearchItem(singer_names=singer_names, song_name=song_name,
                                search_input=search_input, status='Processing')))

        params = urllib.parse.urlencode(
            {'country': 'id', 'lang': 'en', 'sin': 0, 'ein': 30, 'search_input': singer_names + ' ' + song_name})

        url = 'http://api-jooxtt.sanook.com/web-fcgi-bin/web_search?%s' % params

        yield Request(
            url=url,
            callback=self.parse_search_from_joox,
            priority=0,
            meta={'search_input': search_input, 'singer_names': singer_names, 'song_name': song_name}
        )

    def has_joox_search_resp(self, search_input):

        return self.mongo_dao['JooxSearchItem'].find_one({"search_input": search_input}) is not None

    def has_joox_song_detail_resp(self, songid):

        return self.mongo_dao['JooxSongDetailsItem'].find_one({"songid": songid}) is not None
