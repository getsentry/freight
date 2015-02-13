from __future__ import absolute_import, unicode_literals

from ds.models import Task

from .base import Serializer
from .manager import add


@add(Task)
class TaskSerializer(Serializer):
    def serialize(self, item, attrs):
        return {
            'id': str(item.id),
            'status': item.status_label,
        }
