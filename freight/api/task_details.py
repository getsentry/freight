from __future__ import absolute_import

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import db, redis
from freight.models import App, Task, TaskStatus
from freight.notifiers import NotifierEvent
from freight.notifiers.utils import send_task_notifications
from freight.utils.redis import lock


class TaskMixin(object):
    def _get_task(self, app=None, env=None, number=None, task_id=None):
        if task_id:
            return Task.query.get(task_id)
        try:
            app = App.query.filter(App.name == app)[0]
        except IndexError:
            return None
        try:
            return Task.query.filter(
                Task.app_id == app.id,
                Task.environment == env,
                Task.number == number,
            )[0]
        except IndexError:
            return None


class TaskDetailsApiView(ApiView, TaskMixin):
    def get(self, **kwargs):
        """
        Retrive a task.
        """
        task = self._get_task(**kwargs)
        if task is None:
            return self.error('Invalid task', name='invalid_resource', status_code=404)

        return self.respond(serialize(task))

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('status', choices=('cancelled',))

    def put(self, **kwargs):
        task = self._get_task(**kwargs)
        if task is None:
            return self.error('Invalid task', name='invalid_resource', status_code=404)

        with lock(redis, 'task:{}'.format(task.id), timeout=5):
            # we have to refetch in order to ensure lock state changes
            task = Task.query.get(task.id)
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

        return self.respond(serialize(task))
