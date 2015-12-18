from __future__ import absolute_import

from mock import patch

from freight.config import db, queue
from freight.models import TaskStatus
from freight.testutils import TransactionTestCase


class CheckQueueTestCase(TransactionTestCase):
    @patch.object(queue, 'push')
    def test_with_pending_task(self, mock_push):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(
            app=app, user=user, status=TaskStatus.pending,
        )
        db.session.commit()

        queue.apply('freight.jobs.check_queue')

        mock_push.assert_called_once_with('freight.jobs.execute_task', [task.id])

    @patch.object(queue, 'push')
    def test_without_pending_task(self, mock_push):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(
            app=app, user=user, status=TaskStatus.in_progress,
        )
        db.session.commit()

        queue.apply('freight.jobs.check_queue')

        assert not mock_push.called
