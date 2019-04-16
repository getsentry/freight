from unittest.mock import call, patch

from freight.config import db, queue
from freight.models import TaskStatus
from freight import notifiers
from freight.notifiers import NotifierEvent
from freight.notifiers.dummy import DummyNotifier
from freight.testutils import TransactionTestCase


def maybe_pop(collection):
    try:
        return collection.pop(0)
    except IndexError:
        return None


class SendPendingNotificationsTestCase(TransactionTestCase):
    @patch.object(notifiers.queue, "get")
    @patch.object(DummyNotifier, "send")
    def test_with_pending_task(self, mock_send, mock_queue_get):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        self.create_taskconfig(app=app)
        task = self.create_task(app=app, user=user, status=TaskStatus.pending)
        db.session.commit()

        pending = [
            {
                "task": str(task.id),
                "type": "dummy",
                "config": {"foo": "bar"},
                "event": NotifierEvent.TASK_STARTED,
            }
        ]

        mock_queue_get.side_effect = lambda: maybe_pop(pending)

        queue.apply("freight.jobs.send_pending_notifications")

        mock_send.assert_called_once_with(
            task=task, config={"foo": "bar"}, event=NotifierEvent.TASK_STARTED
        )

        assert mock_queue_get.mock_calls == [call(), call()]
