from __future__ import absolute_import

from flask_restful import reqparse

from ds.config import db, redis
from ds.api.base import ApiView
from ds.models import App, Task, TaskStatus
from ds.utils.redis import lock


class TaskIndexApiView(ApiView):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('app')
    post_parser.add_argument('env', default='production')
    post_parser.add_argument('ref')

    def _has_active_task(self, app, env):
        return db.session.query(
            Task.query.filter(
                Task.status.in_([TaskStatus.pending, TaskStatus.in_progress]),
                Task.app_id == app.id,
                Task.environment == env,
            ).exists(),
        ).scalar()

    def post(self):
        """
        Given any constraints for a task are within acceptable bounds, create
        a new task and enqueue it.
        """
        args = self.post_parser.parse_args()

        app = App.query.filter(App.name == args.app).first()
        if not app:
            return self.error('Invalid app')

        with lock(redis, 'task:create:{}'.format(app.id), timeout=5):
            if self._has_active_task(app, args.env):
                return self.error(
                    message='Another task is already in progress for this app',
                    name='locked',
                )

            task = Task(
                app_id=app.id,
                environment=args.env,
                # TODO(dcramer): ref should default based on app config
                ref=args.ref,
            )
            db.session.add(task)
            db.session.flush()

        return self.respond({})
