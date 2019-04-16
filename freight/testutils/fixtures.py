__all__ = ["Fixtures"]

from uuid import uuid4

from freight.config import db
from freight.constants import PROJECT_ROOT
from freight.models import (
    App,
    Repository,
    Task,
    DeploySequence,
    Deploy,
    TaskStatus,
    User,
    TaskConfig,
    TaskConfigType,
)


class Fixtures(object):
    def create_taskconfig(self, app, **kwargs):
        kwargs.setdefault("type", TaskConfigType.deploy)
        kwargs.setdefault("provider", "shell")
        kwargs.setdefault(
            "data",
            {
                "provider_config": {"command": "/bin/echo helloworld"},
                "notifiers": [
                    {"type": "slack", "config": {"webhook_url": "https://example.com"}},
                    {
                        "type": "datadog",
                        "config": {"webhook_url": "https://example.com"},
                    },
                ],
            },
        )

        task_config = TaskConfig(app_id=app.id, **kwargs)
        db.session.add(task_config)
        db.session.commit()

        return task_config

    def create_app(self, repository, **kwargs):
        if not kwargs.get("name"):
            kwargs["name"] = uuid4().hex

        kwargs.setdefault(
            "data",
            {
                "environments": {
                    "production": {"default_ref": "master"},
                    "staging": {"default_ref": "HEAD"},
                }
            },
        )

        app = App(repository_id=repository.id, **kwargs)
        db.session.add(app)
        db.session.commit()

        return app

    def create_task(self, app, user, **kwargs):
        kwargs.setdefault("provider", "shell")
        kwargs.setdefault("ref", "master")
        kwargs.setdefault("sha", "HEAD")
        kwargs.setdefault("status", TaskStatus.in_progress)
        kwargs.setdefault(
            "data", {"provider_config": app.deploy_config.provider_config}
        )
        kwargs.setdefault("params", {"task": "deploy"})

        task = Task(app_id=app.id, user_id=user.id, **kwargs)
        db.session.add(task)
        db.session.commit()

        return task

    def create_deploy(self, task, app, **kwargs):
        kwargs.setdefault("environment", "production")

        deploy = Deploy(
            task_id=task.id,
            app_id=app.id,
            number=DeploySequence.get_clause(app.id, kwargs["environment"]),
            **kwargs,
        )
        db.session.add(deploy)
        db.session.commit()

        return deploy

    def create_repo(self, **kwargs):
        kwargs.setdefault("url", PROJECT_ROOT)
        kwargs.setdefault("vcs", "git")

        repo = Repository(**kwargs)
        db.session.add(repo)
        db.session.commit()

        return repo

    def create_user(self, **kwargs):
        if not kwargs.get("name"):
            kwargs["name"] = uuid4().hex

        user = User(**kwargs)
        db.session.add(user)
        db.session.commit()

        return user
