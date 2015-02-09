from __future__ import absolute_import

import json

from flask import request, Response
from flask.ext.restful import Resource
from urllib import quote

from ds.config import db

LINK_HEADER = '<{uri}&page={page}>; rel="{name}"'


class ApiView(Resource):
    def dispatch_request(self, *args, **kwargs):
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

    def make_links(self, current_page, has_next_page=None):
        links = []
        if current_page > 1:
            links.append(('previous', current_page - 1))

        if has_next_page:
            links.append(('next', current_page + 1))

        querystring = u'&'.join(
            u'{0}={1}'.format(quote(k), quote(v))
            for k, v in request.args.iteritems()
            if k != 'page'
        )
        if querystring:
            base_url = '{0}?{1}'.format(request.base_url, querystring)
        else:
            base_url = request.base_url + '?'

        link_values = []
        for name, page_no in links:
            link_values.append(LINK_HEADER.format(
                uri=base_url,
                page=page_no,
                name=name,
            ))
        return link_values

    def paginate(self, seq, max_per_page=100, on_results=None, **kwargs):
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 25) or 0)
        if max_per_page:
            assert per_page <= max_per_page
        assert page > 0

        if per_page:
            offset = (page - 1) * per_page
            result = list(seq[offset:offset + per_page + 1])
        else:
            offset = 0
            page = 1
            result = list(seq)

        links = self.make_links(
            current_page=page,
            has_next_page=per_page and len(result) > per_page,
        )

        if per_page:
            result = result[:per_page]

        if on_results:
            result = on_results(result)

        return self.respond(result, links=links, **kwargs)
