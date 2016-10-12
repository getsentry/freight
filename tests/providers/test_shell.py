from __future__ import absolute_import

import pytest

from freight import providers
from freight.models import TaskStatus
from freight.providers.utils import parse_provider_config
from freight.exceptions import ApiError
from freight.testutils import TestCase


class ShellProviderBase(TestCase):
    def setUp(self):
        self.provider = providers.get('shell')
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.deploy_config = self.create_taskconfig(app=self.app)
        self.task = self.create_task(app=self.app, user=self.user)
        self.deploy = self.create_deploy(app=self.app, task=self.task)


class ShellProviderTest(ShellProviderBase):
    def test_get_command(self):
        self.task.data['provider_config'] = {
            'command': (
                'env={environment} '
                'task={params[task]} '
                'ref={ref} '
                'sha={sha} '
                'ssh_key={ssh_key} '
                'prev_sha={prev_sha} '
            )
        }
        result = self.provider.get_command(self.deploy, self.task, 'id_rsa').split(' ')
        assert 'env={}'.format(self.deploy.environment) in result
        assert 'ref={}'.format(self.task.ref) in result
        assert 'sha={}'.format(self.task.sha) in result
        assert 'task={}'.format(self.task.params['task']) in result
        assert 'prev_sha=' in result
        assert 'ssh_key=id_rsa' in result

    def test_get_command_with_prev_sha(self):
        prev_sha = 'b' * 40
        prev_task = self.create_task(
            app=self.app,
            user=self.user,
            sha=prev_sha,
            status=TaskStatus.finished,
        )
        self.create_deploy(app=self.app, task=prev_task)

        self.task.data['provider_config'] = {
            'command': (
                'env={environment} '
                'task={params[task]} '
                'ref={ref} '
                'sha={sha} '
                'ssh_key={ssh_key} '
                'prev_sha={prev_sha} '
            )
        }
        result = self.provider.get_command(self.deploy, self.task, 'id_rsa').split(' ')
        assert 'env={}'.format(self.deploy.environment) in result
        assert 'ref={}'.format(self.task.ref) in result
        assert 'sha={}'.format(self.task.sha) in result
        assert 'task={}'.format(self.task.params['task']) in result
        assert 'prev_sha={}'.format(prev_sha) in result
        assert 'ssh_key=id_rsa' in result


class ParseProviderConfigTest(ShellProviderBase):
    def test_minimal(self):
        result = parse_provider_config('shell', {
            'command': '/usr/bin/true',
        })
        assert result['command'] == '/usr/bin/true'

    def test_requires_command(self):
        with pytest.raises(ApiError):
            parse_provider_config('shell', {})

    def test_valid_env(self):
        result = parse_provider_config('shell', {
            'command': '/usr/bin/true',
            'env': {'FOO': 'BAR'},
        })
        assert result['env'] == {'FOO': 'BAR'}

    def test_invalid_env(self):
        with pytest.raises(ApiError):
            parse_provider_config('shell', {
                'command': '/usr/bin/true',
                'env': 'FOO',
            })
