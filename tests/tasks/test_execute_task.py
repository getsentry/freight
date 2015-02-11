from __future__ import absolute_import

from ds.config import celery
from ds.models import LogChunk, TaskStatus
from ds.testutils import TestCase


class ExecuteTaskTestCase(TestCase):
    def test_simple(self):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(app=app, user=user)

        celery.apply("ds.execute_task", task_id=task.id)
        # celery.send_task("ds.execute_task", [task.id])

        assert task.date_started is not None
        assert task.date_finished is not None
        assert task.status == TaskStatus.finished

        logchunks = list(LogChunk.query.filter(
            LogChunk.task_id == task.id,
        ).order_by(LogChunk.offset.asc()))

        assert len(logchunks) == 1
        chunk = logchunks[0]
        assert ">> Running ['/bin/echo', 'helloworld']\n" in chunk.text
        assert chunk.offset == 0
        assert chunk.size == len(chunk.text)
