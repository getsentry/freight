from __future__ import absolute_import

import json

from uuid import uuid4

from freight.models import Task, TaskStatus, TaskName
from freight.testutils import TestCase
from freight import vcs
from freight.utils.workspace import Workspace


class TaskIndexBase(TestCase):
    path = '/api/0/tasks/'

    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        super(TaskIndexBase, self).setUp()


class TaskListTest(TaskIndexBase):
    def setUp(self):
        super(TaskListTest, self).setUp()

    def test_no_filters(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

    def test_status_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
            status=TaskStatus.pending,
        )
        resp = self.client.get(self.path + '?status=pending')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?status=in_progress')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0

    def test_app_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path + '?app=' + self.app.name)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?app=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0

    def test_user_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path + '?user=' + self.user.name)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?user=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0

    def test_env_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path + '?env=' + task.environment)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?env=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0

    def test_ref_filter(self):
        task = self.create_task(
            app=self.app,
            user=self.user,
        )
        resp = self.client.get(self.path + '?ref=' + task.ref)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(task.id)

        resp = self.client.get(self.path + '?ref=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0


class TaskCreateTest(TaskIndexBase):
    def test_simple(self):
        resp = self.client.post(self.path, data={
            'env': 'production',
            'app': self.app.name,
            'ref': 'master',
            'user': self.user.name,
        })
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['id']

        task = Task.query.get(data['id'])
        assert task.environment == 'production'
        assert task.app_id == self.app.id
        assert task.ref == 'master'
        assert task.user_id == self.user.id
        assert task.provider_config == self.app.provider_config
        assert task.notifiers == self.app.notifiers

    # def test_locked(self):
    #     task = self.create_task(
    #         app=self.app,
    #         user=self.user,
    #         status=TaskStatus.pending,
    #     )

    #     resp = self.client.post(self.path, data={
    #         'env': task.environment,
    #         'app': self.app.name,
    #         'ref': 'master',
    #         'user': self.user.name,
    #     })
    #     assert resp.status_code == 400
    #     data = json.loads(resp.data)
    #     assert data['error_name'] == 'locked'

    def test_default_ref(self):
        resp = self.client.post(self.path, data={
            'env': 'staging',
            'app': self.app.name,
            'user': self.user.name,
        })
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['id']

        task = Task.query.get(data['id'])
        assert task.environment == 'staging'
        assert task.app_id == self.app.id
        assert task.ref == 'HEAD'
        assert task.name == TaskName.deploy

    def test_task_target_specific_sha(self):
        vcs_backend = vcs.get(
            self.repo.vcs,
            url=self.repo.url,
            workspace=Workspace(
                path=self.repo.get_path(),
            ),
        )

        shas = vcs_backend.run(['show-ref', '--hash=0'],
                               capture=True).split('\n')

        current_sha = shas[0]

        resp = self.client.post(self.path, data={
            'env': 'staging',
            'app': self.app.name,
            'user': self.user.name,
            'ref': current_sha
        })

        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['id']

        task = Task.query.get(data['id'])

        assert task.environment == 'staging'
        assert task.app_id == self.app.id
        assert task.ref == current_sha
        assert task.name == TaskName.deploy

    def test_task_name(self):
        resp = self.client.post(self.path, data={
            'name': 'collectstatic',
            'env': 'staging',
            'app': self.app.name,
            'user': self.user.name,
        })
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['id']

        task = Task.query.get(data['id'])
        assert task.environment == 'staging'
        assert task.app_id == self.app.id
        assert task.ref == 'HEAD'
        assert task.name == 'collectstatic'

    def test_current_ref_with_no_valids(self):
        resp = self.client.post(self.path, data={
            'env': 'staging',
            'app': self.app.name,
            'user': self.user.name,
            'ref': ':current',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_ref'

    def test_current_ref(self):
        current = self.create_task(
            app=self.app,
            user=self.user,
            environment='staging',
            status=TaskStatus.finished,
            sha=uuid4().hex,
        )

        resp = self.client.post(self.path, data={
            'env': 'staging',
            'app': self.app.name,
            'user': self.user.name,
            'ref': ':current',
        })
        assert resp.status_code == 201, resp.data
        data = json.loads(resp.data)
        assert data['id']

        task = Task.query.get(data['id'])
        assert task.ref == ':current'
        assert task.sha == current.sha

    def test_previous_ref_with_no_valids(self):
        self.create_task(
            app=self.app,
            user=self.user,
            environment='staging',
            status=TaskStatus.finished,
            sha=uuid4().hex,
        )

        resp = self.client.post(self.path, data={
            'env': 'staging',
            'app': self.app.name,
            'user': self.user.name,
            'ref': ':previous',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_ref'

    def test_previous_ref(self):
        previous = self.create_task(
            app=self.app,
            user=self.user,
            environment='staging',
            status=TaskStatus.finished,
            sha=uuid4().hex,
        )
        self.create_task(
            app=self.app,
            user=self.user,
            environment='staging',
            status=TaskStatus.finished,
            sha=uuid4().hex,
        )

        resp = self.client.post(self.path, data={
            'env': 'staging',
            'app': self.app.name,
            'user': self.user.name,
            'ref': ':previous',
        })
        assert resp.status_code == 201, resp.data
        data = json.loads(resp.data)
        assert data['id']

        task = Task.query.get(data['id'])
        assert task.ref == ':previous'
        assert task.sha == previous.sha
