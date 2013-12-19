import sys
import os
import logging
import cgi
import json
import random
import string
import urllib

import tornado.options
import tornado.ioloop
import tornado.web

import tornado.template
import tornado.auth
import tornado.locale
import tornado.escape

from bs4 import BeautifulSoup

from setting import settings
from setting import conn

from controller.base import *


POST_COLORS = ["rgba(169,34,88,0.5)", "rgba(26,28,101,0.5)", "rgba(16,89,113,0.5)", "rgba(169,98,34,0.5)", "rgba(169,34,34,0.5)"]

class MainHandler(BaseHandler):
    def get(self):
        wp_perfix = settings.get("wordpress_prefix", "wp_")

        term = self.get_argument("t", None)
        if term:
            term_record = conn.get("SELECT * FROM %sterms WHERE slug = %s" % (wp_perfix, "%s"), term)
            term_taxonomy = conn.get("SELECT * FROM %sterm_taxonomy WHERE term_id = %s" % (wp_perfix, "%s"), term_record["term_id"])
            object_records = conn.query("SELECT * FROM %sterm_relationships WHERE term_taxonomy_id = %s ORDER BY object_id DESC LIMIT 5" % (wp_perfix, "%s"), term_taxonomy["term_taxonomy_id"])
            self.post_list = conn.query("SELECT * FROM %sposts WHERE post_status = 'publish' AND post_type = 'post' AND ID IN %s ORDER BY ID DESC" % (wp_perfix, "%s"), tuple([i["object_id"] for i in object_records]))
            self.term = "&t=%s" % term
        else:
            self.post_list = conn.query("SELECT * FROM %sposts WHERE post_status = 'publish' AND post_type = 'post' ORDER BY ID DESC LIMIT 5" % wp_perfix)
            self.term = ""

        post_thumbnail_ids = {}
        meta_thumbnails = {}
        post_thumbnails = {}

        postmeta_list = conn.query("SELECT * FROM %spostmeta WHERE meta_key = '_thumbnail_id' AND post_id IN %s" % (wp_perfix, "%s"), tuple([int(i.ID) for i in self.post_list]))
        for postmeta in postmeta_list:
            post_thumbnail_ids[postmeta.post_id] = postmeta.meta_value

        postmeta_list = conn.query("SELECT * FROM %spostmeta WHERE meta_key = '_wp_attached_file' AND post_id IN %s" % (wp_perfix, "%s"), tuple([int(i) for i in post_thumbnail_ids.values()]))
        for postmeta in postmeta_list:
            meta_thumbnails[postmeta.post_id] = postmeta.meta_value

        for k, v in post_thumbnail_ids.iteritems():
            post_thumbnails[k] = meta_thumbnails[long(v)]

        self.post_id_from = self.post_list[-1].ID
        self.carousel_list = []
        carousel_count = 0
        color_count = 0
        for post in self.post_list:
            post.thumbnail = "/wp-content/uploads/%s" % post_thumbnails[post.ID] if post_thumbnails.get(post.ID) else None
            if post.thumbnail and carousel_count < 3:
                self.carousel_list.append(post)
                carousel_count += 1

            soup = BeautifulSoup(post.post_content.split("<!--more-->")[0])
            post.post_excerpt = soup.get_text()

            post.color = POST_COLORS[color_count % len(POST_COLORS)]
            color_count += 1

        self.render('../template/main.html')


class MoreAPIHandler(BaseHandler):
    def get(self):
        wp_perfix = settings.get("wordpress_prefix", "wp_")

        from_id = int(self.get_argument("from", ""))
        term = self.get_argument("t", None)
        if term:
            term_record = conn.get("SELECT * FROM %sterms WHERE slug = %s" % (wp_perfix, "%s"), term)
            term_taxonomy = conn.get("SELECT * FROM %sterm_taxonomy WHERE term_id = %s" % (wp_perfix, "%s"), term_record["term_id"])
            object_records = conn.query("SELECT * FROM %sterm_relationships WHERE term_taxonomy_id = %s AND object_id < %s ORDER BY object_id DESC LIMIT 5" % (wp_perfix, "%s", "%s"), term_taxonomy["term_taxonomy_id"], from_id)
            post_list = conn.query("SELECT * FROM %sposts WHERE post_status = 'publish' AND post_type = 'post' AND ID IN %s ORDER BY ID DESC" % (wp_perfix, "%s"), tuple([i["object_id"] for i in object_records]))
            self.term = "&t=%s" % term
        else:
            post_list = conn.query("SELECT * FROM %sposts WHERE post_status = 'publish' AND post_type = 'post' AND ID < %s ORDER BY ID DESC LIMIT 5" % (wp_perfix, "%s"), from_id)

        post_thumbnail_ids = {}
        meta_thumbnails = {}
        post_thumbnails = {}

        postmeta_list = conn.query("SELECT * FROM %spostmeta WHERE meta_key = '_thumbnail_id' AND post_id IN %s" % (wp_perfix, "%s"), tuple([int(i.ID) for i in post_list]))
        for postmeta in postmeta_list:
            post_thumbnail_ids[postmeta.post_id] = postmeta.meta_value

        postmeta_list = conn.query("SELECT * FROM %spostmeta WHERE meta_key = '_wp_attached_file' AND post_id IN %s" % (wp_perfix, "%s"), tuple([int(i) for i in post_thumbnail_ids.values()]))
        for postmeta in postmeta_list:
            meta_thumbnails[postmeta.post_id] = postmeta.meta_value

        for k, v in post_thumbnail_ids.iteritems():
            post_thumbnails[k] = meta_thumbnails[long(v)]

        post_list_json = []
        color_count = 0
        for post in post_list:
            soup = BeautifulSoup(post.post_content.split("<!--more-->")[0])
            post_json = {}
            post_json["post_excerpt"] = soup.get_text()
            post_json["post_title"] = post.post_title
            post_json["post_name"] = post.post_name
            post_json["thumbnail"] = "/wp-content/uploads/%s" % post_thumbnails[post.ID] if post_thumbnails.get(post.ID) else None
            post_json["color"] = POST_COLORS[color_count % len(POST_COLORS)]
            color_count += 1

            post_list_json.append(post_json)

        self.finish({"list":post_list_json, "post_id_from":post_list[-1].ID if post_list else 0})


class PostHandler(BaseHandler):
    def get(self, post_name):
        wp_perfix = settings.get("wordpress_prefix", "wp_")

        self.post = conn.get("SELECT * FROM %sposts WHERE post_status = 'publish' AND post_type = 'post' AND post_name = %s" % (wp_perfix, "%s"), tornado.escape.url_escape(post_name))
        if not self.post:
            raise tornado.web.HTTPError(404)

        self.render('../template/post.html')


