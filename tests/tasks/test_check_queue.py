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
        deploy_config = self.create_taskconfig(app=app)
        task = self.create_task(
            app=app, user=user, status=TaskStatus.pending,
        )
        deploy = self.create_deploy(
            app=app, task=task,
        )
        db.session.commit()

        queue.apply('freight.jobs.check_queue')

        mock_push.assert_called_once_with('freight.jobs.execute_deploy', [deploy.id])

    @patch.object(queue, 'push')
    def test_without_pending_task(self, mock_push):
        user = self.create_user()
        repo = self.create_repo()
        app = self.create_app(repository=repo)
        deploy_config = self.create_taskconfig(app=app)
        task = self.create_task(
            app=app, user=user, status=TaskStatus.in_progress,
        )
        deploy = self.create_deploy(
            app=app, task=task,
        )
        db.session.commit()

        queue.apply('freight.jobs.check_queue')

        assert not mock_push.called

    @patch.object(queue, 'push')
    def test_inprogress_pending_task(self, mock_push):
        user = self.create_user()
        repo = self.create_repo()

        app_1 = self.create_app(repository=repo)
        deploy_config_1 = self.create_taskconfig(app=app_1)
        task_1 = self.create_task(
            app=app_1, user=user, status=TaskStatus.in_progress,
        )
        deploy_1 = self.create_deploy(
            app=app_1, task=task_1,
        )
        db.session.commit()

        queue.apply('freight.jobs.check_queue')

        assert not mock_push.called

        app_2 = self.create_app(repository=repo)
        deploy_config_2 = self.create_taskconfig(app=app_2)
        task_2 = self.create_task(
            app=app_2, user=user, status=TaskStatus.pending,
        )
        deploy_2 = self.create_deploy(
            app=app_2, task=task_2,
        )
        db.session.commit()

        queue.apply('freight.jobs.check_queue')

        mock_push.assert_called_once_with('freight.jobs.execute_deploy', [deploy_2.id])
