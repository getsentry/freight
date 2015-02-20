from __future__ import absolute_import, unicode_literals

import freight
import urlparse

from freight.utils.auth import get_current_user

from flask import current_app, redirect, render_template, url_for
from flask.views import MethodView


class IndexView(MethodView):
    def __init__(self, login_url):
        self.login_url = login_url
        super(IndexView, self).__init__()

    def get(self, path=''):
        user = get_current_user()
        if not user:
            return redirect(url_for(self.login_url))

        if current_app.config['SENTRY_DSN'] and False:
            parsed = urlparse.urlparse(current_app.config['SENTRY_DSN'])
            dsn = '%s://%s@%s/%s' % (
                parsed.scheme.rsplit('+', 1)[-1],
                parsed.username,
                parsed.hostname + (':%s' % (parsed.port,) if parsed.port else ''),
                parsed.path,
            )
        else:
            dsn = None

        return render_template('index.html', **{
            'SENTRY_PUBLIC_DSN': dsn,
            'VERSION': freight.get_version(),
        })
