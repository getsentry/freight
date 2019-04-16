from flask.helpers import send_from_directory
from flask.views import MethodView


class IndexView(MethodView):
    def __init__(self, root):
        self.root = root
        super(IndexView, self).__init__()

    def get(self, path=""):
        return send_from_directory(self.root, "index.html")
