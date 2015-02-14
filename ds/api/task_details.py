from __future__ import absolute_import, unicode_literals

from ds.api.base import ApiView
from ds.api.serializer import serialize
from ds.models import Task


class TaskDetailsApiView(ApiView):
    def get(self, task_id):
        """
        Retrive a task.
        """
        task = Task.query.get(task_id)
        if task is None:
            return self.error('Invalid task', name='invalid_resource', status_code=404)

        return self.respond(serialize(task))
