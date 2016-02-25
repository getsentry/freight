from __future__ import absolute_import

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import db, redis
from freight.models import App, Task, Deploy, TaskStatus
from freight.notifiers import NotifierEvent
from freight.notifiers.utils import send_task_notifications
from freight.utils.redis import lock


class DeployMixin(object):
    def _get_deploy(self, app=None, env=None, number=None, deploy_id=None):
        if deploy_id:
            return Deploy.query.get(deploy_id)
        try:
            app = App.query.filter(App.name == app)[0]
        except IndexError:
            return None
        try:
            return Deploy.query.filter(
                Deploy.app_id == app.id,
                Deploy.environment == env,
                Deploy.number == number,
            )[0]
        except IndexError:
            return None


class DeployDetailsApiView(ApiView, DeployMixin):
    def get(self, **kwargs):
        """
        Retrive a task.
        """
        deploy = self._get_deploy(**kwargs)
        if deploy is None:
            return self.error('Invalid deploy', name='invalid_resource', status_code=404)

        return self.respond(serialize(deploy))

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('status', choices=('cancelled',))

    def put(self, **kwargs):
        deploy = self._get_deploy(**kwargs)
        if deploy is None:
            return self.error('Invalid deploy', name='invalid_resource', status_code=404)

        with lock(redis, 'deploy:{}'.format(deploy.id), timeout=5):
            # we have to refetch in order to ensure lock state changes
            deploy = Deploy.query.get(deploy.id)
            task = Task.query.get(deploy.task_id)
            args = self.put_parser.parse_args()
            if args.status:
                assert task.status in (TaskStatus.pending, TaskStatus.in_progress)
                assert args.status == 'cancelled'
                did_cancel = task.status == TaskStatus.pending
                task.status = TaskStatus.cancelled

            db.session.add(task)
            db.session.commit()

        if args.status and did_cancel:
            send_task_notifications(task, NotifierEvent.TASK_FINISHED)

        return self.respond(serialize(deploy))
