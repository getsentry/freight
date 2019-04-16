from freight.testutils import TestCase


class CatchallTest(TestCase):
    def test_simple(self):
        path = "/api/0/not-a-real-endpoint"

        for method in ("get", "post", "put", "delete", "patch"):
            resp = getattr(self.client, method)(path)
            assert resp.status_code == 404
            assert b"".join(resp.data.splitlines()) == b'{"error": "Not Found"}'
