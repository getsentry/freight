from __future__ import absolute_import

from flask import current_app as app
from flask.helpers import send_from_directory
from flask.views import MethodView


class StaticView(MethodView):
    def __init__(self, root, cache_timeout=0):
        self.root = root
        self.cache_timeout = 30

    def get(self, filename):
        return send_from_directory(
            self.root, filename, cache_timeout=self.cache_timeout)
