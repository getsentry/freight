from __future__ import absolute_import

from flask_restful import Api, Resource


class ApiController(Api):
    pass


class ApiCatchall(Resource):
    def get(self, path):
        return {'error': 'Not Found'}, 404

    post = get
    put = get
    delete = get
    patch = get
