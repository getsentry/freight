from __future__ import absolute_import

from ds.constants import PROJECT_ROOT
from ds.testutils import TestCase
from ds.tasks import execute_task


class ExecuteTaskTestCase(TestCase):
    def test_simple(self):
        user = self.create_user()
        repo = self.create_repo(url='file:///' + PROJECT_ROOT)
        app = self.create_app(repository=repo)
        task = self.create_task(app=app, user=user)

        execute_task(task_id=task.id)
