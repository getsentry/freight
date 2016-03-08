from __future__ import absolute_import

import json

from flask_restful import reqparse, inputs

from freight import checks, vcs
from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.config import db, redis
from freight.exceptions import CheckError, CheckPending
from freight.models import (
    App, Repository, Task, Deploy, DeploySequence, TaskStatus, User,
    TaskConfig, TaskConfigType,
)
from freight.notifiers import NotifierEvent
from freight.notifiers.utils import send_task_notifications
from freight.utils.auth import get_current_user
from freight.utils.redis import lock
from freight.utils.workspace import Workspace


class DeployIndexApiView(ApiView):
    def _get_internal_ref(self, app, env, ref):
        # find the most recent green deploy for this app
        if ref == ':current':
            return app.get_current_sha(env)

        # the previous stable ref (before current)
        if ref == ':previous':
            current_sha = app.get_current_sha(env)

            if not current_sha:
                return

            return app.get_previous_sha(env, current_sha=current_sha)
        raise ValueError('Unknown ref: {}'.format(ref))

    get_parser = reqparse.RequestParser()
    get_parser.add_argument('app', location='args')
    get_parser.add_argument('user', location='args')
    get_parser.add_argument('env', location='args')
    get_parser.add_argument('ref', location='args')
    get_parser.add_argument('status', location='args', action='append')

    def get(self):
        """
        Retrieve a list of deploys.

        If any parameters are invalid the result will simply be an empty list.
        """
        args = self.get_parser.parse_args()

        qs_filters = []

        if args.app:
            app = App.query.filter(App.name == args.app).first()
            if not app:
                return self.respond([])
            qs_filters.append(Deploy.app_id == app.id)

        if args.user:
            user = User.query.filter(User.name == args.user).first()
            if not user:
                return self.respond([])
            qs_filters.append(Task.user_id == user.id)

        if args.env:
            qs_filters.append(Deploy.environment == args.env)

        if args.ref:
            qs_filters.append(Task.ref == args.ref)

        if args.status:
            status_list = map(TaskStatus.label_to_id, args.status)
            qs_filters.append(Task.status.in_(status_list))

        deploy_qs = Deploy.query.filter(*qs_filters).order_by(Deploy.id.desc())

        return self.paginate(deploy_qs, on_results=serialize)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('app', required=True)
    post_parser.add_argument('params', type=json.loads)
    post_parser.add_argument('user')
    post_parser.add_argument('env', default='production')
    post_parser.add_argument('ref')
    post_parser.add_argument('force', default=False, type=inputs.boolean)

    def post(self):
        """
        Given any constraints for a task are within acceptable bounds, create
        a new task and enqueue it.
        """
        args = self.post_parser.parse_args()

        user = get_current_user()
        if not user:
            username = args.user
            if not username:
                return self.error('Missing required argument "user"', status_code=400)

            with lock(redis, 'user:create:{}'.format(username), timeout=5):
                # TODO(dcramer): this needs to be a get_or_create pattern and
                # ideally moved outside of the lock
                user = User.query.filter(User.name == username).first()
                if not user:
                    user = User(name=username)
                    db.session.add(user)
                    db.session.flush()
        elif args.user:
            return self.error('Cannot specify user when using session authentication.', status_code=400)

        app = App.query.filter(App.name == args.app).first()
        if not app:
            return self.error('Invalid app', name='invalid_resource', status_code=404)

        deploy_config = TaskConfig.query.filter(
            TaskConfig.app_id == app.id,
            TaskConfig.type == TaskConfigType.deploy,
        ).first()
        if not deploy_config:
            return self.error('Missing deploy config', name='missing_conf', status_code=404)

        params = None

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

        ref = args.ref or app.get_default_ref(args.env)

        # look for our special refs (prefixed via a colon)
        # TODO(dcramer): this should be supported outside of just this endpoint
        if ref.startswith(':'):
            sha = self._get_internal_ref(app, args.env, ref)
            if not sha:
                return self.error('Invalid ref', name='invalid_ref', status_code=400)
        else:
            try:
                sha = vcs_backend.get_sha(ref)
            except vcs.UnknownRevision:
                return self.error('Invalid ref', name='invalid_ref', status_code=400)

        if args.params is not None:
            params = args.params

        if not args.force:
            for check_config in deploy_config.checks:
                check = checks.get(check_config['type'])
                try:
                    check.check(app, sha, check_config['config'])
                except CheckPending:
                    pass
                except CheckError as e:
                    return self.error(
                        message=unicode(e),
                        name='check_failed',
                    )

        with lock(redis, 'deploy:create:{}'.format(app.id), timeout=5):
            task = Task(
                app_id=app.id,
                # TODO(dcramer): ref should default based on app config
                ref=ref,
                sha=sha,
                params=params,
                status=TaskStatus.pending,
                user_id=user.id,
                provider=deploy_config.provider,
                data={
                    'force': args.force,
                    'provider_config': deploy_config.provider_config,
                    'notifiers': deploy_config.notifiers,
                    'checks': deploy_config.checks,
                },
            )
            db.session.add(task)
            db.session.flush()
            db.session.refresh(task)

            deploy = Deploy(
                task_id=task.id,
                app_id=app.id,
                environment=args.env,
                number=DeploySequence.get_clause(app.id, args.env),
            )
            db.session.add(deploy)
            db.session.commit()

            send_task_notifications(task, NotifierEvent.TASK_QUEUED)

        return self.respond(serialize(deploy), status_code=201)
