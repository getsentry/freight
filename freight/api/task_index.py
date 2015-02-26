from __future__ import absolute_import, unicode_literals

from flask_restful import reqparse, inputs

from freight import checks, vcs
from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import celery, db, redis
from freight.exceptions import CheckFailed
from freight.models import (
    App, Repository, Task, TaskName, TaskSequence, TaskStatus, User
)
from freight.utils.redis import lock
from freight.utils.workspace import Workspace


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
    get_parser.add_argument('status', location='args', action='append')

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
            status_list = map(TaskStatus.label_to_id, args.status)
            qs_filters.append(Task.status.in_(status_list))

        task_qs = Task.query.filter(*qs_filters).order_by(Task.id.desc())

        return self.paginate(task_qs, on_results=serialize)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('app', required=True)
    post_parser.add_argument('user', required=True)
    post_parser.add_argument('env', default='production')
    post_parser.add_argument('ref', default='master')
    post_parser.add_argument('force', default=False, type=inputs.boolean)

    def post(self):
        """
        Given any constraints for a task are within acceptable bounds, create
        a new task and enqueue it.
        """
        args = self.post_parser.parse_args()

        app = App.query.filter(App.name == args.app).first()
        if not app:
            return self.error('Invalid app', name='invalid_resource', status_code=404)

        repo = Repository.query.get(app.repository_id)

        workspace = Workspace(
            path=repo.get_path(),
        )

        vcs_backend = vcs.get(
            repo.vcs,
            url=repo.url,
            workspace=workspace,
        )

        with lock(redis, 'repo:update:{}'.format(repo.id)):
            vcs_backend.clone_or_update()

        try:
            sha = vcs_backend.describe(args.ref)
        except vcs.UnknownRevision:
            return self.error('Invalid ref', name='invalid_ref', status_code=400)

        if not args.force:
            for check_config in app.checks:
                check = checks.get(check_config['type'])
                try:
                    check.check(app, sha, check_config['config'])
                except CheckFailed as e:
                    return self.error(
                        message=unicode(e),
                        name='check_failed',
                    )

        with lock(redis, 'task:create:{}'.format(app.id), timeout=5):
            # TODO(dcramer): this needs to be a get_or_create pattern and
            # ideally moved outside of the lock
            user = User.query.filter(User.name == args.user).first()
            if not user:
                user = User(name=args.user)
                db.session.add(user)
                db.session.flush()

            if not args.force and self._has_active_task(app, args.env):
                return self.error(
                    message='Another task is already in progress for this app/environment',
                    name='locked',
                )

            task = Task(
                app_id=app.id,
                environment=args.env,
                number=TaskSequence.get_clause(app.id, args.env),
                name=TaskName.deploy,
                # TODO(dcramer): ref should default based on app config
                ref=args.ref,
                sha=sha,
                status=TaskStatus.pending,
                user_id=user.id,
                provider=app.provider,
                data={
                    'force': args.force,
                    'provider_config': app.provider_config,
                    'notifiers': app.notifiers,
                    'checks': app.checks,
                },
            )
            db.session.add(task)
            db.session.commit()

        celery.send_task("freight.execute_task", [task.id])

        return self.respond(serialize(task), status_code=201)
