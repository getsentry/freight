from __future__ import absolute_import

__all__ = ['build_session', 'delete', 'get', 'post', 'put']

import freight
import requests

USER_AGENT = 'freight/{version} (https://github.com/getsentry/freight)'.format(
    version=freight.VERSION,
),


def build_session():
    session = requests.Session()
    session.headers.update({'User-Agent': USER_AGENT})
    return session


def delete(*args, **kwargs):
    session = build_session()
    return session.delete(*args, **kwargs)


def get(*args, **kwargs):
    session = build_session()
    return session.get(*args, **kwargs)


def post(*args, **kwargs):
    session = build_session()
    return session.post(*args, **kwargs)


def put(*args, **kwargs):
    session = build_session()
    return session.put(*args, **kwargs)
