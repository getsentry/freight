from __future__ import absolute_import

from ds.config import celery
from ds.testutils import TestCase


class ExecuteTaskTestCase(TestCase):
    def test_simple(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(app=app, user=user)

        celery.apply("ds.execute_task", task_id=task.id)
        # celery.send_task("ds.execute_task", [task.id])
