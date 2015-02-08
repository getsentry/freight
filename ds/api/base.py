from __future__ import absolute_import

import json

from flask import Response
from flask.ext.restful import Resource

from ds.config import db

LINK_HEADER = '<{uri}&page={page}>; rel="{name}"'


def error(message, http_code=400):
    return {
        'error': message,
    }, http_code


class APIView(Resource):
    def dispatch_request(self, *args, **kwargs):
        try:
            response = super(APIView, self).dispatch_request(*args, **kwargs)
        except Exception:
            db.session.rollback()
            raise
        else:
            db.session.commit()
        return response

    def respond(self, context, status_code=200, links=None):
        response = Response(
            json.dumps(context),
            mimetype='application/json',
            status=status_code,
        )

        if links:
            response.headers['Link'] = ', '.join(links)

        return response
