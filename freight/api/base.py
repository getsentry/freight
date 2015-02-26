from __future__ import absolute_import, unicode_literals

import json

from flask import current_app, request, Response
from flask_restful import Resource
from urllib import quote

from freight.config import db
from freight.exceptions import ApiError
from freight.utils.auth import get_current_user

LINK_HEADER = '<{uri}&cursor={cursor}>; rel="{name}"'


class ApiView(Resource):
    def is_authorized(self):
        current_user = get_current_user()
        if current_user:
            return True

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
        except ApiError as e:
            return self.error(
                message=e.message,
                name=e.name,
                status_code=e.status_code,
            )

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

    def build_cursor_link(self, name, cursor):
        querystring = u'&'.join(
            u'{0}={1}'.format(quote(k), quote(v))
            for k, v in request.args.iteritems()
            if k != 'cursor'
        )
        base_url = request.base_url
        if querystring:
            base_url = '{0}?{1}'.format(base_url, querystring)
        else:
            base_url = base_url + '?'

        return LINK_HEADER.format(
            uri=base_url,
            cursor=str(cursor),
            name=name,
        )

    def make_links(self, current_page, has_next_page=None):
        links = []
        if current_page > 1:
            links.append((self.build_cursor_link('previous', current_page - 1)))

        if has_next_page:
            links.append((self.build_cursor_link('next', current_page + 1)))

        return links

    def paginate(self, seq, max_limit=100, on_results=None, **kwargs):
        cursor = int(request.args.get('cursor', 1))
        limit = int(request.args.get('limit', 25) or 0)
        if max_limit:
            assert limit <= max_limit

        if cursor:
            offset = (cursor - 1) * limit
            result = list(seq[offset:offset + limit + 1])
        else:
            offset = 0
            page = 1
            result = list(seq)

        links = self.make_links(
            current_page=cursor,
            has_next_page=limit and len(result) > limit,
        )

        if limit:
            result = result[:limit]

        if on_results:
            result = on_results(result)

        return self.respond(result, links=links, **kwargs)
