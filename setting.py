import os

import json
import torndb

settings = {
    #"xsrf_cookies": True,
    "static_path": os.path.join(os.path.dirname(__file__), "static/"),
    "cookie_secret": "VaNttOomjAGcMacLx3SXG994pyYh7pNnp671mp3vabc=",
    "wordpress_prefix": "wp_",
    "login_url": "/login",
    "debug": True,
}


conn = torndb.Connection("127.0.0.1", "wordpress", "root", "root")

