from __future__ import absolute_import

import json

from freight.config import db
from freight.models import TaskStatus
from freight.testutils import TestCase


class TaskDetailsBase(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.task = self.create_task(app=self.app, user=self.user)
        self.path = '/api/0/tasks/{}/'.format(self.task.id)
        super(TaskDetailsBase, self).setUp()


class TaskDetailsTest(TaskDetailsBase):
    def test_simple(self):
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['id'] == str(self.task.id)


class TaskUpdateTest(TaskDetailsBase):
    def test_simple(self):
        resp = self.client.put(self.path, data={'status': 'cancelled'})
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['id'] == str(self.task.id)
        db.session.expire(self.task)
        db.session.refresh(self.task)
        assert self.task.status == TaskStatus.cancelled
