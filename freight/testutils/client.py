__all__ = ["AuthenticatedTestClient"]

from flask import current_app
from flask.testing import FlaskClient


class AuthenticatedTestClient(FlaskClient):
    def open(self, *args, **kwargs):
        kwargs.setdefault("headers", {})
        kwargs["headers"].setdefault(
            "Authorization", f"Key {current_app.config['API_KEY']}"
        )
        return FlaskClient.open(self, *args, **kwargs)
