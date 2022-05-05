import os

from freight.api.base import ApiView

from urllib.parse import urlparse


class ConfigApiView(ApiView):
    def get(self):
        """
        Returns a configuration object
        """
        dsn = os.environ.get("SENTRY_DSN")
        if dsn:
            parsed = urlparse(dsn)
            dsn = "{}://{}@{}/{}".format(
                parsed.scheme.rsplit("+", 1)[-1],
                parsed.username,
                parsed.hostname + (f":{parsed.port}" if parsed.port else ""),
                parsed.path,
            )

        return self.respond(
            {"SENTRY_PUBLIC_DSN": dsn, "VERSION": "0.0.0"}, status_code=201
        )
