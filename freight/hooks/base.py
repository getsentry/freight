from __future__ import absolute_import

__all__ = ['Hook']

from flask import current_app
from flask.testing import FlaskClient


class HookClient(FlaskClient):
    def open(self, *args, **kwargs):
        kwargs.setdefault('headers', {})
        kwargs['headers'].setdefault(
            'Authorization', 'Key {}'.format(current_app.config['API_KEY'])
        )
        return FlaskClient.open(self, *args, **kwargs)


class Hook(object):
    def client(self):
        return HookClient(current_app, current_app.response_class)

    def deploy(self, app, env):
        raise NotImplementedError
