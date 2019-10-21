from functools import reduce
import json

from freight.testutils import TestCase


class StatsBase(TestCase):
    path = "/api/0/stats/"

    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        super(StatsBase, self).setUp()


class StatsTest(StatsBase):
    def setUp(self):
        super(StatsTest, self).setUp()

        self.app_a = self.create_app(repository=self.repo, name="foo")
        self.app_b = self.create_app(repository=self.repo, name="bar")
        self.create_taskconfig(app=self.app_a)
        self.create_taskconfig(app=self.app_b)
        self.create_task(app=self.app_a, user=self.user)
        self.create_task(app=self.app_a, user=self.user)
        self.create_task(app=self.app_a, user=self.user)

        self.create_task(app=self.app_b, user=self.user)
        self.create_task(app=self.app_b, user=self.user)

    def test_simple(self):
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert reduce((lambda x, y: x + y), list(map(lambda x: x[1], data))) == 5

    def test_app_filter(self):
        resp = self.client.get(self.path + "?app=" + self.app_b.name)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert reduce((lambda x, y: x + y), list(map(lambda x: x[1], data))) == 2
