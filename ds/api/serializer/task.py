from __future__ import absolute_import

from ds.models import Task

from .base import register, Serializer


@register(Task)
class TaskSerializer(Serializer):
    def serialize(self, item, attrs):
        return {
            'id': str(item.id),
            'status': item.status_label,
        }
