from __future__ import absolute_import

from flask.ext.restful import reqparse

from ds.api.base import APIView
# from ds.models import Task


class TaskIndexAPIView(APIView):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('app')
    post_parser.add_argument('env', default='production')
    post_parser.add_argument('ref')

    def post(self):
        """
        Given any constraints for a task are within acceptable bounds, create
        a new task and enqueue it.
        """
        args = self.post_parser.parse_args()

        return self.respond({})
