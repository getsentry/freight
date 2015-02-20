from __future__ import absolute_import, unicode_literals

__all__ = ['Fixtures']

from uuid import uuid4

from freight.config import db
from freight.constants import PROJECT_ROOT
from freight.models import App, Repository, Task, TaskSequence, TaskStatus, User


class Fixtures(object):
    def create_app(self, repository, **kwargs):
        if not kwargs.get('name'):
            kwargs['name'] = uuid4().hex

        kwargs.setdefault('provider', 'shell')
        kwargs.setdefault('data', {
            'provider_config': {
                'command': '/bin/echo helloworld',
            },
            'notifiers': [
                {
                    'type': 'slack',
                    'config': {'webhook_url': 'https://example.com'},
                },
            ],
        })

        app = App(repository_id=repository.id, **kwargs)
        db.session.add(app)
        db.session.commit()

        return app

    def create_task(self, app, user, **kwargs):
        kwargs.setdefault('provider', 'shell')
        kwargs.setdefault('name', 'deploy')
        kwargs.setdefault('ref', 'master')
        kwargs.setdefault('environment', 'production')
        kwargs.setdefault('sha', 'HEAD')
        kwargs.setdefault('status', TaskStatus.in_progress)
        kwargs.setdefault('data', {'provider_config': app.provider_config})

        task = Task(
            app_id=app.id,
            user_id=user.id,
            number=TaskSequence.get_clause(app.id, kwargs['environment']),
            **kwargs
        )
        db.session.add(task)
        db.session.commit()

        return task

    def create_repo(self, **kwargs):
        kwargs.setdefault('url', PROJECT_ROOT)
        kwargs.setdefault('vcs', 'git')

        repo = Repository(**kwargs)
        db.session.add(repo)
        db.session.commit()

        return repo

    def create_user(self, **kwargs):
        if not kwargs.get('name'):
            kwargs['name'] = uuid4().hex

        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()

        return user
