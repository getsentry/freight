from __future__ import absolute_import

import json

from flask import current_app, request, Response
from flask.ext.restful import Resource

from ds.config import db

LINK_HEADER = '<{uri}&page={page}>; rel="{name}"'


class ApiView(Resource):
    def is_authorized(self):
        try:
            auth = request.headers['Authorization']
        except KeyError:
            return False

        try:
            method, payload = auth.split(' ', 1)
        except ValueError:
            return False

        if method != 'Key':
            return False

        if payload != current_app.config['API_KEY']:
            return False

        return True

    def dispatch_request(self, *args, **kwargs):
        if not self.is_authorized():
            return self.error(
                message='You are not authorized.',
                name='unauthorized',
            )

        try:
            response = super(ApiView, self).dispatch_request(*args, **kwargs)
        except Exception:
            db.session.rollback()
            raise
        else:
            db.session.commit()
        return response

    def error(self, message, name=None, status_code=400):
        context = {
            'error': message,
        }
        if name:
            context['error_name'] = name

        return self.respond(context, status_code=status_code)

    def respond(self, context, status_code=200, links=None):
        response = Response(
            json.dumps(context),
            mimetype='application/json',
            status=status_code,
        )

        if links:
            response.headers['Link'] = ', '.join(links)

        return response
