from __future__ import absolute_import, unicode_literals

from ds import providers
from ds.testutils import TestCase


class ShellProviderBase(TestCase):
    def setUp(self):
        self.provider = providers.get('shell')
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.task = self.create_task(app=self.app, user=self.user)


class ShellProviderTest(ShellProviderBase):
    def test_get_command(self):
        self.task.data['provider_config'] = {
            'command': 'env={environment} task={task} ref={ref} sha={sha} ssh_key={ssh_key}'
        }
        result = self.provider.get_command(self.task, 'id_rsa').split(' ')
        assert 'env={}'.format(self.task.environment) in result
        assert 'ref={}'.format(self.task.ref) in result
        assert 'sha={}'.format(self.task.sha) in result
        assert 'task={}'.format(self.task.name) in result
        assert 'ssh_key=id_rsa' in result
