from __future__ import absolute_import, unicode_literals

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import db
from freight.models import Task, TaskStatus


class TaskDetailsApiView(ApiView):
    def get(self, task_id):
        """
        Retrive a task.
        """
        task = Task.query.get(task_id)
        if task is None:
            return self.error('Invalid task', name='invalid_resource', status_code=404)

        return self.respond(serialize(task))

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('status', choices=('cancelled',))

    def put(self, task_id):
        task = Task.query.get(task_id)
        if task is None:
            return self.error('Invalid task', name='invalid_resource', status_code=404)

        args = self.put_parser.parse_args()
        if args.status:
            assert task.status in (TaskStatus.pending, TaskStatus.in_progress)
            assert args.status == 'cancelled'
            task.status = TaskStatus.cancelled
        db.session.add(task)
        db.session.commit()

        return self.respond(serialize(task))
