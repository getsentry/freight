from __future__ import absolute_import

import hmac
from hashlib import sha256

from flask import current_app

from freight.testutils import TestCase


class WebhooksViewTest(TestCase):
    def make_path(self, hook, action, app, env='production', digest=None):
        key = '{}/{}/{}/{}'.format(hook, action, app, env)
        if digest is None:
            api_key = current_app.config['API_KEY']
            digest = hmac.new(api_key, key, sha256).hexdigest()
        return '/webhooks/{}/{}/'.format(key, digest)

    def test_bad_digest(self):
        resp = self.client.post(
            self.make_path('github', 'deploy', 'test', digest='xxxx'),
        )
        assert resp.status_code == 403, resp.data

    def test_invalid_hook(self):
        resp = self.client.post(
            self.make_path('xxx', 'deploy', 'test'),
        )
        assert resp.status_code == 404, resp.data

    def test_invalid_app(self):
        resp = self.client.post(
            self.make_path('github', 'deploy', 'test'),
        )
        assert resp.status_code == 404, resp.data
