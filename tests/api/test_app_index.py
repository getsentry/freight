from __future__ import absolute_import

import json

from freight.models import App
from freight.testutils import TestCase


class AppIndexBase(TestCase):
    path = '/api/0/apps/'

    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        super(AppIndexBase, self).setUp()


class AppListTest(AppIndexBase):
    def setUp(self):
        super(AppListTest, self).setUp()

    def test_no_filters(self):
        app = self.create_app(
            repository=self.repo,
        )
        self.create_taskconfig(app=app)
        resp = self.client.get(self.path)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(app.id)

    def test_name_filter(self):
        app = self.create_app(
            repository=self.repo,
            name='foobar',
        )
        self.create_taskconfig(app=app)
        resp = self.client.get(self.path + '?name=' + app.name)
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 1
        assert data[0]['id'] == str(app.id)

        resp = self.client.get(self.path + '?name=nothing')
        assert resp.status_code == 200
        data = json.loads(resp.data)
        assert len(data) == 0


class AppCreateTest(AppIndexBase):
    def test_simple(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true", "timeout": 50}',
            'notifiers': '[{"type": "slack", "config": {"webhook_url": "https://example.com"}}]',
            'checks': '[{"type": "github", "config": {"contexts": ["travisci"], "repo": "getsentry/freight"}}]',
            'repository': 'git@example.com:repo-name.git',
            'environments': '{"staging": {"default_ref": "develop"}}',
        })
        assert resp.status_code == 201
        data = json.loads(resp.data)
        assert data['id']

        app = App.query.get(data['id'])
        deploy_config = app.deploy_config
        assert app.name == 'foobar'
        assert deploy_config.provider == 'shell'
        assert deploy_config.provider_config['command'] == '/usr/bin/true'
        assert deploy_config.provider_config['timeout'] == 50
        assert deploy_config.notifiers == [
            {'type': 'slack', 'config': {'webhook_url': 'https://example.com'}},
        ]
        assert len(deploy_config.checks) == 1
        assert deploy_config.checks[0]['type'] == 'github'
        assert deploy_config.checks[0]['config'] == {'contexts': ['travisci'], 'repo': 'getsentry/freight'}
        assert len(app.environments) == 1
        assert app.environments['staging'] == {'default_ref': 'develop'}

    def test_invalid_provider(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'invalid',
            'provider_config': '{"command": "/usr/bin/true"}',
            'repository': 'git@example.com:repo-name.git',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_provider'

    def test_invalid_provider_config(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{}',
            'repository': 'git@example.com:repo-name.git',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_provider'

    def test_invalid_notifier(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true"}',
            'notifiers': '[{"type": "invalid"}]',
            'repository': 'git@example.com:repo-name.git',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_notifier'

    def test_invalid_notifier_config(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true"}',
            'notifiers': '[{"type": "slack", "config": {}}]',
            'repository': 'git@example.com:repo-name.git',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_notifier'

    def test_invalid_check(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true"}',
            'repository': 'git@example.com:repo-name.git',
            'checks': '[{"type": "invalid"}]',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_check'

    def test_invalid_check_config(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true"}',
            'repository': 'git@example.com:repo-name.git',
            'checks': '[{"type": "github", "config": {}}]',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_check'

    def test_invalid_environments_type(self):
        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true"}',
            'repository': 'git@example.com:repo-name.git',
            'environments': '[{"type": "github", "config": {}}]',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_environment'

        resp = self.client.post(self.path, data={
            'name': 'foobar',
            'provider': 'shell',
            'provider_config': '{"command": "/usr/bin/true"}',
            'repository': 'git@example.com:repo-name.git',
            'environments': '{"foo": []}',
        })
        assert resp.status_code == 400
        data = json.loads(resp.data)
        assert data['error_name'] == 'invalid_environment'
