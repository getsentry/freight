from flask import current_app

from freight import get_version
from freight.api.base import ApiView

from urllib.parse import urlparse


class ConfigApiView(ApiView):
    def get(self):
        """
        Returns a configuration object
        """

        if current_app.config["SENTRY_DSN"]:
            parsed = urlparse(current_app.config["SENTRY_DSN"])
            dsn = "{}://{}@{}/{}".format(
                parsed.scheme.rsplit("+", 1)[-1],
                parsed.username,
                parsed.hostname + (f":{parsed.port}" if parsed.port else ""),
                parsed.path,
            )
        else:
            dsn = None

        return self.respond(
            {"SENTRY_PUBLIC_DSN": dsn, "VERSION": get_version()}, status_code=201
        )
