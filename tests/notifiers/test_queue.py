from __future__ import absolute_import

from freight.models import TaskStatus
from freight.notifiers import NotifierEvent, NotificationQueue
from freight.testutils import TestCase


class NotificationQueueTest(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.task = self.create_task(
            app=self.app,
            user=self.user,
            status=TaskStatus.finished,
        )

    def test_simple(self):
        queue = NotificationQueue(delay=0)
        queue.put(
            task=self.task,
            type='dummy',
            config={'foo': 'bar'},
            event=NotifierEvent.TASK_STARTED,
        )
        result = queue.get()
        assert result == {
            'task': str(self.task.id),
            'type': 'dummy',
            'config': {'foo': 'bar'},
            'event': NotifierEvent.TASK_STARTED,
        }

        result = queue.get()
        assert result is None
