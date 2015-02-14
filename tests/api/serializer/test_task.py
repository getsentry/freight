from __future__ import absolute_import, unicode_literals

from ds.api.serializer import serialize
from ds.models import TaskStatus
from ds.testutils import TestCase


class TaskSerializerTest(TestCase):
    def test_locked(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(app=app, user=user, status=TaskStatus.pending)

        result = serialize(task)
        assert result['id'] == str(task.id)
        assert result['status'] == 'pending'
        assert result['ref'] == task.ref
        assert result['sha'] == task.sha
        assert result['environment'] == task.environment
        assert result['app']['id'] == str(app.id)
        assert result['app']['name'] == app.name
