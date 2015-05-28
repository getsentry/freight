from __future__ import absolute_import

import json
import mock

from freight.models import App
from freight.testutils import TestCase


class AppDetailsBase(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.path = '/api/0/apps/{}/'.format(self.app.id)
        super(AppDetailsBase, self).setUp()


class AppDetailsTest(AppDetailsBase):
    def test_simple(self):
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['id'] == str(self.app.id)


class AppUpdateTest(AppDetailsBase):
    def test_simple(self):
        resp = self.client.put(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true", "timeout": 50}',
            'notifiers': '[{"type": "slack", "config": {"webhook_url": "https://example.com"}}]',
            'checks': '[{"type": "github", "config": {"contexts": ["travisci"], "repo": "getsentry/freight"}}]',
            'repository': 'git@example.com:repo-name.git',
            'environments': '{"staging": {"default_ref": "develop"}}',
        })
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['id'] == str(self.app.id)

        app = App.query.get(self.app.id)
        assert app.name == 'foobar'
        assert app.provider == 'shell'
        assert app.provider_config['command'] == '/usr/bin/true'
        assert app.provider_config['timeout'] == 50
        assert app.notifiers == [
            {'type': 'slack', 'config': {'webhook_url': 'https://example.com'}},
        ]

        assert len(app.checks) == 1
        assert app.checks[0]['type'] == 'github'
        assert app.checks[0]['config'] == {'contexts': ['travisci'], 'repo': 'getsentry/freight'}
        assert len(app.environments) == 1
        assert app.environments['staging'] == {'default_ref': 'develop'}

    def test_no_params(self):
        resp = self.client.put(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert data['id'] == str(self.app.id)

        app = App.query.get(self.app.id)
        assert app.name == self.app.name
        assert app.provider == self.app.provider
        assert app.provider_config == self.app.provider_config

    def test_invalid_provider(self):
        resp = self.client.put(self.path, data={
            'provider': 'dummy',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_provider'

    def test_invalid_provider_config(self):
        resp = self.client.put(self.path, data={
            'provider': 'shell',
            'provider_config': '{}',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_provider'

    def test_invalid_notifier(self):
        resp = self.client.put(self.path, data={
            'notifiers': '[{"type": "dummy"}]',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_notifier'

    def test_invalid_notifier_config(self):
        resp = self.client.put(self.path, data={
            'notifiers': '[{"type": "slack", "config": {}}]',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_notifier'

    def test_invalid_check(self):
        resp = self.client.put(self.path, data={
            'checks': '[{"type": "dummy"}]',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_check'

    def test_invalid_check_config(self):
        resp = self.client.put(self.path, data={
            'checks': '[{"type": "github", "config": {}}]',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_check'

    def test_invalid_environments_type(self):
        resp = self.client.put(self.path, data={
            'environments': '[{"type": "github", "config": {}}]',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_environment'

        resp = self.client.put(self.path, data={
            'environments': '{"foo": []}',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_environment'


class AppDeleteTest(AppDetailsBase):
    @mock.patch('freight.config.celery.send_task')
    def test_simple(self, mock_send_task):
        self.create_task(app=self.app, user=self.user)
        resp = self.client.delete(self.path)
        assert resp.status_code == 200

        mock_send_task.assert_called_once_with('freight.delete_object', kwargs={'model': 'App', 'app_id': self.app.id})
