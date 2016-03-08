from __future__ import absolute_import

from mock import patch

from freight.models import TaskStatus
from freight.notifiers import NotifierEvent, queue
from freight.notifiers.utils import (
    clear_task_notifications, send_task_notifications
)
from freight.testutils import TestCase


class SendTaskNotificationsTest(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.deploy_config = self.create_taskconfig(app=self.app)
        self.task = self.create_task(
            app=self.app,
            user=self.user,
            status=TaskStatus.finished,
            data={
                'notifiers': [{
                    'type': 'dummy',
                    'config': {},
                }],
            }
        )

    @patch.object(queue, 'put')
    def test_task_started(self, mock_put):
        send_task_notifications(self.task, NotifierEvent.TASK_STARTED)
        mock_put.assert_called_once_with(
            task=self.task,
            type='dummy',
            config={},
            event=NotifierEvent.TASK_STARTED,
        )

    @patch.object(queue, 'put')
    def test_task_finished(self, mock_put):
        send_task_notifications(self.task, NotifierEvent.TASK_FINISHED)
        assert not mock_put.called


class ClearTaskNotificationsTest(TestCase):
    def setUp(self):
        self.user = self.create_user()
        self.repo = self.create_repo()
        self.app = self.create_app(repository=self.repo)
        self.deploy_config = self.create_taskconfig(app=self.app)
        self.task = self.create_task(
            app=self.app,
            user=self.user,
            status=TaskStatus.finished,
            data={
                'notifiers': [{
                    'type': 'dummy',
                    'config': {},
                }],
            }
        )

    @patch.object(queue, 'remove')
    def test_simple(self, mock_remove):
        clear_task_notifications(self.task)
        mock_remove.assert_called_once_with(
            task=self.task,
            type='dummy',
        )
