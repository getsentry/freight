from __future__ import absolute_import

from datetime import datetime, timedelta
from sqlalchemy.sql import func

from freight.config import db
from freight.models import App, Task, Deploy, TaskStatus, User

from .base import Serializer
from .manager import add, serialize


@add(Deploy)
class DeploySerializer(Serializer):
    def get_attrs(self, item_list):
        apps = {
            a.id: a
            for a in App.query.filter(
                App.id.in_(set(i.app_id for i in item_list)),
            )
        }

        tasks = {
            t.id: t
            for t in Task.query.filter(
                Task.id.in_(set(i.task_id for i in item_list)),
            )
        }

        estimatedDurations = dict(db.session.query(
            Task.app_id,
            func.avg(Task.date_finished - Task.date_started),
        ).filter(
            Task.date_finished > datetime.utcnow() - timedelta(days=7),
            Task.status == TaskStatus.finished,
        ).group_by(Task.app_id))

        user_ids = set(tasks[d.task_id].user_id for d in item_list)
        if user_ids:
            user_map = {
                u.id: u
                for u in User.query.filter(User.id.in_(user_ids))
            }
        else:
            user_map = {}

        attrs = {}
        for item in item_list:
            estimatedDuration = estimatedDurations.get(tasks[item.task_id].app_id)
            if estimatedDuration:
                estimatedDuration = estimatedDuration.total_seconds()

            attrs[item] = {
                'app': apps[item.app_id],
                'user': user_map.get(tasks[item.task_id].user_id),
                'estimatedDuration': estimatedDuration,
            }
        return attrs

    def serialize(self, item, attrs):
        app = attrs['app']

        task = Task.query.filter(Task.id == item.task_id).first()

        return {
            'id': str(item.id),
            'name': '{}/{}#{}'.format(app.name, item.environment, item.number),
            'app': {
                'id': str(app.id),
                'name': app.name,
            },
            'user': serialize(attrs['user']),
            'environment': item.environment,
            'sha': task.sha,
            'ref': task.ref,
            'number': item.number,
            'status': task.status_label,
            'duration': task.duration,
            'estimatedDuration': task.duration or attrs['estimatedDuration'],
            'dateCreated': self.format_datetime(task.date_created),
            'dateStarted': self.format_datetime(task.date_started),
            'dateFinished': self.format_datetime(task.date_finished),
        }
