from __future__ import absolute_import

__all__ = ['AuthenticatedTestClient']

from flask import current_app
from flask.testing import FlaskClient


class AuthenticatedTestClient(FlaskClient):
    def open(self, *args, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault(
            'Authorization', 'Key {}'.format(current_app.config['API_KEY'])
        )
        return FlaskClient.open(self, *args, **kwargs)
