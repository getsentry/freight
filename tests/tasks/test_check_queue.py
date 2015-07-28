from __future__ import absolute_import

from mock import patch

from freight.config import celery, db
from freight.models import TaskStatus
from freight.testutils import TransactionTestCase


class CheckQueueTestCase(TransactionTestCase):
    @patch.object(celery, 'send_task')
    def test_with_pending_task(self, mock_send_task):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(
            app=app, user=user, status=TaskStatus.pending,
        )
        db.session.commit()

        celery.apply("freight.check_queue")

        mock_send_task.assert_called_once_with('freight.execute_task', [task.id])

    @patch.object(celery, 'send_task')
    def test_without_pending_task(self, mock_send_task):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        task = self.create_task(
            app=app, user=user, status=TaskStatus.in_progress,
        )
        db.session.commit()

        celery.apply("freight.check_queue")

        assert not mock_send_task.called
