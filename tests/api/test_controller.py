from __future__ import absolute_import

from freight.testutils import TestCase


class CatchallTest(TestCase):
    def test_simple(self):
        path = '/api/0/not-a-real-endpoint'

        for method in ('get', 'post', 'put', 'delete', 'patch'):
            resp = getattr(self.client, method)(path)
            assert resp.status_code == 404
            assert ''.join(resp.data.splitlines()) == '{"error": "Not Found"}'
