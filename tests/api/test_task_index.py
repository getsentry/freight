from __future__ import absolute_import

from ds.models import TaskStatus
from ds.testutils import TestCase


class TaskCreateTest(TestCase):
    def test_locked(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(app=app, user=user, status=TaskStatus.pending)
        path = '/api/0/tasks/'

        resp = self.client.post(path, data={
            'env': task.environment,
            'app': app.name,
            'ref': 'master',
        })
        assert resp.status_code == 400
