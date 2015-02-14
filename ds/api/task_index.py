from __future__ import absolute_import, unicode_literals

from flask_restful import reqparse

from ds.config import celery, db, redis
from ds.api.base import ApiView
from ds.api.serializer import serialize
from ds.models import App, Task, TaskName, TaskSequence, TaskStatus, User
from ds.utils.redis import lock


class TaskIndexApiView(ApiView):
    def _has_active_task(self, app, env):
        return db.session.query(
            Task.query.filter(
                Task.status.in_([TaskStatus.pending, TaskStatus.in_progress]),
                Task.app_id == app.id,
                Task.environment == env,
            ).exists(),
        ).scalar()

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('app', location='args')
    get_parser.add_argument('user', location='args')
    get_parser.add_argument('env', location='args')
    get_parser.add_argument('ref', location='args')
    get_parser.add_argument('status', location='args')

    def get(self):
        """
        Retrieve a list of tasks.

        If any parameters are invalid the result will simply be an empty list.
        """
        args = self.get_parser.parse_args()

        qs_filters = []

        if args.app:
            app = App.query.filter(App.name == args.app).first()
            if not app:
                return self.respond([])
            qs_filters.append(Task.app_id == app.id)

        if args.user:
            user = User.query.filter(User.name == args.user).first()
            if not user:
                return self.respond([])
            qs_filters.append(Task.user_id == user.id)

        if args.env:
            qs_filters.append(Task.environment == args.env)

        if args.ref:
            qs_filters.append(Task.ref == args.ref)

        if args.status:
            status = TaskStatus.label_to_id(args.status)
            qs_filters.append(Task.status == status)

        task_qs = Task.query.filter(*qs_filters).order_by(Task.id.desc())

        return self.paginate(task_qs, on_results=serialize)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('app', required=True)
    post_parser.add_argument('user', required=True)
    post_parser.add_argument('env', default='production')
    post_parser.add_argument('ref')

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
            # TODO(dcramer): this needs to be a get_or_create pattern and
            # ideally moved outside of the lock
            user = User.query.filter(User.name == args.user).first()
            if not user:
                user = User(name=args.user)
                db.session.add(user)
                db.session.flush()

            if self._has_active_task(app, args.env):
                return self.error(
                    message='Another task is already in progress for this app',
                    name='locked',
                )

            task = Task(
                app_id=app.id,
                environment=args.env,
                number=TaskSequence.get_clause(app.id, args.env),
                name=TaskName.deploy,
                # TODO(dcramer): ref should default based on app config
                ref=args.ref,
                status=TaskStatus.pending,
                user_id=user.id,
                provider=app.provider,
                data={
                    'provider_config': app.provider_config,
                    'notifiers': app.data.get('notifiers', []),
                },
            )
            db.session.add(task)
            db.session.commit()

        celery.send_task("ds.execute_task", [task.id])

        return self.respond(serialize(task), status_code=201)
