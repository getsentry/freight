from __future__ import absolute_import, unicode_literals

from freight.models import App, Task

from .base import Serializer
from .manager import add


@add(Task)
class TaskSerializer(Serializer):
    def get_attrs(self, item_list):
        apps = {
            a.id: a
            for a in App.query.filter(
                App.id.in_(set(i.app_id for i in item_list)),
            )
        }

        attrs = {}
        for item in item_list:
            attrs[item] = {'app': apps[item.app_id]}
        return attrs

    def serialize(self, item, attrs):
        app = attrs['app']

        return {
            'id': str(item.id),
            'app': {
                'id': str(app.id),
                'name': app.name,
            },
            'environment': item.environment,
            'sha': item.sha,
            'ref': item.ref,
            'number': item.number,
            'status': item.status_label,
            'duration': item.duration,
            'dateCreated': self.format_datetime(item.date_created),
            'dateStarted': self.format_datetime(item.date_started),
            'dateFinished': self.format_datetime(item.date_finished),
        }
