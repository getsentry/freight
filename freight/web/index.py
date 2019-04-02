from __future__ import absolute_import

from flask.helpers import send_from_directory
from flask.views import MethodView


class IndexView(MethodView):
    def __init__(self, login_url, root):
        self.login_url = login_url
        self.root = root
        super(IndexView, self).__init__()

    def get(self, path=''):
        return send_from_directory(
            self.root,
            "index.html",
        )
