import json

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.checks.utils import parse_checks_config
from freight.config import db, queue
from freight.environments.utils import parse_environments_config
from freight.models import App, Repository, TaskConfig, TaskConfigType
from freight.notifiers.utils import parse_notifiers_config
from freight.providers.utils import parse_provider_config


class AppDetailsApiView(ApiView):
    def get(self, app):
        app = App.query.filter(App.name == app).first()
        if app is None:
            return self.error("Invalid app", name="invalid_resource", status_code=404)

        deploy_config = TaskConfig.query.filter(
            TaskConfig.app_id == app.id, TaskConfig.type == TaskConfigType.deploy
        ).first()
        if deploy_config is None:
            return self.error(
                "Missing deploy config", name="missing_conf", status_code=404
            )

        context = serialize(app)
        context.update(
            {
                "provider": deploy_config.provider,
                "provider_config": deploy_config.provider_config,
                "notifiers": deploy_config.notifiers,
                "checks": deploy_config.checks,
            }
        )

        return self.respond(context)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument("name")
    put_parser.add_argument("repository")
    put_parser.add_argument("provider")
    put_parser.add_argument("providerConfig", type=json.loads)
    put_parser.add_argument("notifiers", type=json.loads)
    put_parser.add_argument("checks", type=json.loads)
    put_parser.add_argument("environments", type=json.loads)

    def put(self, app):
        """
        Update an app.
        """
        args = self.put_parser.parse_args()

        app = App.query.filter(App.name == app).first()
        if app is None:
            return self.error("Invalid app", name="invalid_resource", status_code=404)

        # For backwards compatibility, we assume that we need a deploy TaskConfig
        # on the app at all times.
        deploy_config = TaskConfig.query.filter(
            TaskConfig.app_id == app.id, TaskConfig.type == TaskConfigType.deploy
        ).first()
        if deploy_config is None:
            deploy_config = TaskConfig(app_id=app.id, type=TaskConfigType.deploy)
            db.session.add(deploy_config)
            db.session.flush()

        if args.provider or args.providerConfig:
            if args.provider is not None:
                provider = args.provider
            else:
                provider = deploy_config.provider

            if args.providerConfig is not None:
                provider_config = args.providerConfig
            else:
                provider_config = deploy_config.provider_config

            deploy_config.provider = provider
            deploy_config.data["provider_config"] = parse_provider_config(
                provider, provider_config
            )

        if args.notifiers is not None:
            deploy_config.data["notifiers"] = parse_notifiers_config(args.notifiers)

        if args.checks is not None:
            deploy_config.data["checks"] = parse_checks_config(args.checks)

        if args.environments is not None:
            app.data["environments"] = parse_environments_config(args.environments)

        if args.name:
            app.name = args.name

        # TODO(dcramer): this needs to be a get_or_create pattern
        if args.repository:
            repo = Repository.query.filter(Repository.url == args.repository).first()
            if repo is None:
                repo = Repository(url=args.repository, vcs="git")
                db.session.add(repo)
                db.session.flush()
            app.repository_id = repo.id

        db.session.add(app)
        db.session.add(deploy_config)
        db.session.commit()

        context = serialize(app)
        context.update(
            {
                "provider": deploy_config.provider,
                "provider_config": deploy_config.provider_config,
                "notifiers": deploy_config.notifiers,
                "checks": deploy_config.checks,
            }
        )

        return self.respond(context)

    def delete(self, app):
        """
        Delete an app.
        """
        app = App.query.filter(App.name == app).first()
        if app is None:
            return self.error("Invalid app", name="invalid_resource", status_code=404)

        queue.push(
            "freight.jobs.delete_object", kwargs={"model": "App", "object_id": app.id}
        )

        return self.respond({"id": str(app.id)})
