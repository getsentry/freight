from __future__ import absolute_import

from datetime import datetime, timedelta
from sqlalchemy.sql import func

from freight.config import db
from freight.models import App, Task, TaskStatus, User

from .base import Serializer
from .manager import add, serialize


@add(Task)
class TaskSerializer(Serializer):
    def get_attrs(self, item_list):
        apps = {
            a.id: a
            for a in App.query.filter(
                App.id.in_(set(i.app_id for i in item_list)),
            )
        }

        estimatedDurations = dict(db.session.query(
            Task.app_id,
            func.avg(Task.date_finished - Task.date_started),
        ).filter(
            Task.date_finished > datetime.utcnow() - timedelta(days=7),
            Task.status == TaskStatus.finished,
        ).group_by(Task.app_id))

        user_ids = set(t.user_id for t in item_list)
        if user_ids:
            user_map = {
                u.id: u
                for u in User.query.filter(User.id.in_(user_ids))
            }
        else:
            user_map = {}

        attrs = {}
        for item in item_list:
            estimatedDuration = estimatedDurations.get(item.app_id)
            if estimatedDuration:
                estimatedDuration = estimatedDuration.total_seconds()

            attrs[item] = {
                'app': apps[item.app_id],
                'user': user_map.get(item.user_id),
                'estimatedDuration': estimatedDuration,
            }
        return attrs

    def serialize(self, item, attrs):
        app = attrs['app']

        return {
            'id': str(item.id),
            'app': {
                'id': str(app.id),
                'name': app.name,
            },
            'user': serialize(attrs['user']),
            'environment': item.environment,
            'sha': item.sha,
            'ref': item.ref,
            'number': item.number,
            'status': item.status_label,
            'duration': item.duration,
            'estimatedDuration': item.duration or attrs['estimatedDuration'],
            'dateCreated': self.format_datetime(item.date_created),
            'dateStarted': self.format_datetime(item.date_started),
            'dateFinished': self.format_datetime(item.date_finished),
        }
