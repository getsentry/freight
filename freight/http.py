__all__ = ["build_session", "delete", "get", "post", "put"]

import freight
import certifi
import json
from urllib3 import PoolManager as _PoolManager
from urllib3.exceptions import HTTPError

from flask import current_app

USER_AGENT = f"freight/{freight.VERSION} (https://github.com/getsentry/freight)"


class PoolManager(_PoolManager):
    def delete(self, *args, **kwargs):
        return self.request("DELETE", *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.request("GET", *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request("POST", *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request("PUT", *args, **kwargs)

    def request(self, *args, **kwargs):
        kwargs.setdefault("headers", {})
        kwargs["headers"].update(self.headers)
        if "json" in kwargs:
            json_data = kwargs.pop("json")
            kwargs["body"] = json.dumps(json_data).encode("utf8")
            kwargs["headers"]["Content-Type"] = "application/json"
        if "params" in kwargs:
            kwargs["fields"] = kwargs.pop("params")
        return super().request(*args, **kwargs)


def build_session():
    return PoolManager(headers={"User-Agent": USER_AGENT}, ca_certs=certifi.where())


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


def raise_for_status(resp):
    error_type = ""
    if 400 <= resp.status < 500:
        error_type = "Client"
    elif 500 <= resp.status < 600:
        error_type = "Server"

    if error_type:
        raise HTTPError(
            f"{resp.status} {error_type} Error: {resp.reason} for url: {resp._request_url}"
        )
