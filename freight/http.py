__all__ = ["build_session", "delete", "get", "post", "put"]

import requests

from flask import current_app

USER_AGENT = f"freight (https://github.com/getsentry/freight)"


def build_session():
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
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


def absolute_uri(path):
    base = current_app.config["FREIGHT_URL"]
    if path.startswith(("https:", "http:")):
        return path
    return f"{base}{path}"
