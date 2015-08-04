from __future__ import absolute_import

from mock import call, patch

from freight.config import celery, db
from freight.models import TaskStatus
from freight.notifiers import NotifierEvent, queue
from freight.notifiers.dummy import DummyNotifier
from freight.testutils import TransactionTestCase


def maybe_pop(collection):
    try:
        return collection.pop(0)
    except IndexError:
        return None


class SendPendingNotificationsTestCase(TransactionTestCase):
    @patch.object(queue, 'get')
    @patch.object(DummyNotifier, 'send')
    def test_with_pending_task(self, mock_send, mock_queue_get):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(
            app=app, user=user, status=TaskStatus.pending,
        )
        db.session.commit()

        pending = [{
            'task': str(task.id),
            'type': 'dummy',
            'config': {'foo': 'bar'},
            'event': NotifierEvent.TASK_STARTED,
        }]

        mock_queue_get.side_effect = lambda: maybe_pop(pending)

        celery.apply("freight.send_pending_notifications")

        mock_send.assert_called_once_with(
            task=task,
            config={'foo': 'bar'},
            event=NotifierEvent.TASK_STARTED,
        )

        assert mock_queue_get.mock_calls == [
            call(),
            call(),
        ]
