from __future__ import absolute_import

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import db, redis
from freight.models import App, Task, TaskStatus
from freight.notifiers import NotifierEvent
from freight.notifiers.utils import send_task_notifications
from freight.utils.redis import lock


class BaseMixin(object):
    def _get_obj(self, app=None, env=None, number=None, obj_model=None, **kwargs):
        obj_id = [v for k, v in kwargs.iteritems() if k.endswith('_id')]
        if obj_id:
            return obj_model.query.get(obj_id[0])
        try:
            app = App.query.filter(App.name == app)[0]
        except IndexError:
            return None
        try:
            # HACK(jtcunning): Only difference in build and deploy.
            try:
                return obj_model.query.filter(
                    obj_model.app_id == app.id,
                    obj_model.environment == env,
                    obj_model.number == number,
                )[0]
            except AttributeError:
                return obj_model.query.filter(
                    obj_model.app_id == app.id,
                    obj_model.number == number,
                )[0]
        except IndexError:
            return None


class BaseDetailsApiView(ApiView, BaseMixin):
    def __init__(self):
        raise NotImplementedError
        # self.obj_model = Task

    def get(self, **kwargs):
        """
        Retrive a task.
        """
        kwargs['obj_model'] = self.obj_model
        obj = self._get_obj(**kwargs)
        if obj is None:
            return self.error('Invalid obj', name='invalid_resource', status_code=404)

        return self.respond(serialize(obj))

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('status', choices=('cancelled',))

    def put(self, **kwargs):
        kwargs['obj_model'] = self.obj_model
        obj = self._get_obj(**kwargs)
        if obj is None:
            return self.error('Invalid obj', name='invalid_resource', status_code=404)

        with lock(redis, '{}:{}'.format(type(obj).__name__, obj.id), timeout=5):
            # we have to refetch in order to ensure lock state changes
            obj = self.obj_model.query.get(obj.id)
            task = Task.query.get(obj.task_id)
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

        return self.respond(serialize(obj))
