from configparser import ConfigParser
from pymongo import MongoClient

class MongoDao(object):

    def __init__(self):

        config = ConfigParser()
        config.read('joox_search_and_detail/configs/config.ini')

        mongodb_config = config['MongoDb']
        self.conn = MongoClient(mongodb_config['host'])
        self.conn[mongodb_config['db']].authenticate(mongodb_config['username'], mongodb_config['password'])

        self.db = self.conn[mongodb_config['db']]

    def get_instance(self):
        return self.db
