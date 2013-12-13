import urllib

import tornado.web
import tornado.locale
from tornado import httpclient

#from amazon_ses import AmazonSES
#from amazon_ses import EmailMessage

from setting import settings


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        user_json = self.get_secure_cookie("user")
        if not user_json: return None
        return tornado.escape.json_decode(user_json)

    def get_access_token(self):
        return None

    #def get_user_locale(self):
    #    return tornado.locale.get("zh_CN")
