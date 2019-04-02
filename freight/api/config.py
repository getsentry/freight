from __future__ import absolute_import

from flask import current_app, redirect, url_for

from freight import get_version
from freight.api.base import ApiView

from urlparse import urlparse


class ConfigApiView(ApiView):
    def get(self):
        """
        Returns a configuration object
        """

        if not self.is_authorized():
            return redirect(url_for('login'))

        if current_app.config['SENTRY_DSN']:
            parsed = urlparse(current_app.config['SENTRY_DSN'])
            dsn = '%s://%s@%s/%s' % (
                parsed.scheme.rsplit('+', 1)[-1],
                parsed.username,
                parsed.hostname + (':%s' % (parsed.port,) if parsed.port else ''),
                parsed.path,
            )
        else:
            dsn = None

        return self.respond({
            'SENTRY_PUBLIC_DSN': dsn,
            'VERSION': get_version(),

        }, status_code=201)
