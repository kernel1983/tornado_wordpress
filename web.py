import sys
import os
import logging
import cgi

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/vendor')

os.chdir(os.path.dirname(os.path.abspath(__file__)))

#import wsgiref.simple_server
#import wsgiref.handlers
#import tornado.wsgi
import tornado.options
import tornado.ioloop
import tornado.web
import tornado.template
#import tornado.database
import tornado.auth
import tornado.locale

from setting import settings
from setting import conn

from controller import wordpress

handlers = [
    (r"/", wordpress.MainHandler),
    (r"/api/more", wordpress.MoreAPIHandler),
    (r"/static/(.*)", tornado.web.StaticFileHandler, dict(path=settings['static_path'], default_filename='index.html')),
    (r"/(.*)/", wordpress.PostHandler),
    (r"/(.*)", wordpress.PostHandler),
]


if __name__ == "__main__":
    tornado.locale.load_translations(os.path.join(os.path.dirname(__file__), "csv_translations"))
    tornado.locale.set_default_locale("zh_CN")
    tornado.options.define("port", default=8000, help="Run server on a specific port", type=int)
    tornado.options.parse_command_line()
    application = tornado.web.Application(handlers, **settings)
    application.listen(tornado.options.options.port)
    tornado.ioloop.IOLoop.instance().start()

