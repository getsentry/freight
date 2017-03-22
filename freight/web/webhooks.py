from __future__ import absolute_import

import hmac
from hashlib import sha256

from flask import current_app, Response
from flask.views import MethodView

from freight import hooks
from freight.models import App
from freight.exceptions import InvalidHook


class WebhooksView(MethodView):
    def respond(self, body='', status_code=200):
        rv = Response(body)
        rv.status_code = status_code
        return rv

    def get(self, *args, **kwargs):
        rv = Response()
        rv.status_code = 405
        return rv

    def post(self, hook, action, app, env, digest):
        expected = hmac.new(current_app.config['API_KEY'], '%s/%s/%s/%s' % (
            hook, action, app, env,
        ), sha256).hexdigest()
        if not hmac.compare_digest(expected, digest.encode('utf8')):
            return self.respond(status_code=403)

        try:
            hook = hooks.get(hook)
        except InvalidHook:
            return self.respond('Invalid hook', status_code=404)

        if action != 'deploy':
            return self.respond('Unknown action', status_code=404)

        app = App.query.filter(App.name == app).first()
        if app is None:
            return self.respond('Invalid app', status_code=404)

        try:
            return hook.deploy(app, env)
        except NotImplementedError:
            return self.respond(status_code=404)
