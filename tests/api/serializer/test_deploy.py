from __future__ import absolute_import

from freight.api.serializer import serialize
from freight.models import TaskStatus
from freight.testutils import TestCase


class DeploySerializerTest(TestCase):
    def test_locked(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        self.create_taskconfig(app=app)
        task = self.create_task(app=app, user=user, status=TaskStatus.pending)
        deploy = self.create_deploy(app=app, task=task)

        result = serialize(deploy)
        assert result['id'] == str(deploy.id)
        assert result['status'] == 'pending'
        assert result['ref'] == task.ref
        assert result['sha'] == task.sha
        assert result['environment'] == deploy.environment
        assert result['number'] == deploy.number
        assert result['app']['id'] == str(app.id)
        assert result['app']['name'] == app.name
