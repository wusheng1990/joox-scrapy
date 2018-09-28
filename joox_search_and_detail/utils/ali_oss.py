import oss2
from configparser import ConfigParser

class OssDao(object):

    def __init__(self):

        config = ConfigParser()
        config.read('joox_search_and_detail/configs/config.ini')

        oss_config = config['OSS']
        self.bucket=oss_config['bucket']
        accessKeyID=oss_config['accessKeyID']
        accessKeySecret=oss_config['accessKeySecret']
        ecsEndPoint = oss_config['ecsEndPoint']
        self.internetEndPoint = oss_config['internetEndPoint']

        auth = oss2.Auth(accessKeyID, accessKeySecret)
        self.instance = oss2.Bucket(auth, ecsEndPoint, self.bucket)

    def get_instance(self):
        return self.instance

    def get_url_prefix(self):
        return 'http://' + self.bucket + '.' + self.internetEndPoint + '/'

