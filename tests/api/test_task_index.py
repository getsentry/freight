from __future__ import absolute_import

import json

from ds.models import Task, TaskStatus
from ds.testutils import TestCase


class TaskCreateTest(TestCase):
    def test_simple(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        path = '/api/0/tasks/'

        resp = self.client.post(path, data={
            'env': 'production',
            'app': app.name,
            'ref': 'master',
            'user': user.name,
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['id']

        task = Task.query.get(data['id'])
        assert task.environment == 'production'
        assert task.app_id == app.id
        assert task.ref == 'master'
        assert task.user_id == user.id

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
            'user': user.name,
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'locked'
