from __future__ import absolute_import

import json

from freight.config import db
from freight.models import LogChunk
from freight.testutils import TestCase


class TaskLogBase(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.task = self.create_task(app=self.app, user=self.user)
        self.path = '/api/0/tasks/{}/log/'.format(self.task.id)

        offset = 0
        for char in 'hello world':
            db.session.add(LogChunk(
                task_id=self.task.id,
                text=char,
                size=len(char),
                offset=offset,
            ))
            offset += len(char)
        db.session.commit()

        super(TaskLogBase, self).setUp()


class TaskLogTest(TaskLogBase):
    def test_simple(self):
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['nextOffset'] == 11
        assert data['text'] == 'hello world'

    def test_limit_and_offset(self):
        resp = self.client.get(self.path + '?limit=1')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['text'] == 'h'
        assert data['nextOffset'] == 1

        resp = self.client.get(self.path + '?limit=1&offset=1')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['text'] == 'e'
        assert data['nextOffset'] == 2

    def test_tail(self):
        resp = self.client.get(self.path + '?offset=-1&limit=1')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['text'] == 'd'
        assert data['nextOffset'] == 11

        resp = self.client.get(self.path + '?offset=-1&limit=11')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['text'] == 'hello world'
        assert data['nextOffset'] == 11
