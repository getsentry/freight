from __future__ import absolute_import, unicode_literals

import json

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.checks.utils import parse_checks_config
from freight.config import celery, db
from freight.models import App, Repository
from freight.notifiers.utils import parse_notifiers_config
from freight.providers.utils import parse_provider_config


class AppDetailsApiView(ApiView):
    def get(self, app_id):
        app = App.query.get(app_id)
        if app is None:
            return self.error('Invalid app', name='invalid_resource', status_code=404)

        context = serialize(app)
        context.update({
            'provider': app.provider,
            'provider_config': app.provider_config,
            'notifiers': app.notifiers,
            'checks': app.checks,
        })

        return self.respond(context)

    put_parser = reqparse.RequestParser()
    put_parser.add_argument('name')
    put_parser.add_argument('repository')
    put_parser.add_argument('provider')
    put_parser.add_argument('provider_config', type=json.loads)
    put_parser.add_argument('notifiers', type=json.loads)
    put_parser.add_argument('checks', type=json.loads)

    def put(self, app_id):
        """
        Update an app.
        """
        args = self.put_parser.parse_args()

        app = App.query.get(app_id)
        if app is None:
            return self.error('Invalid app', name='invalid_resource', status_code=404)

        if args.provider or args.provider_config:
            if args.provider is not None:
                provider = args.provider
            else:
                provider = app.provider

            if args.provider_config is not None:
                provider_config = args.provider_config
            else:
                provider_config = app.provider_config

            app.provider = provider
            app.data['provider_config'] = parse_provider_config(
                provider, provider_config
            )

        if args.notifiers is not None:
            app.data['notifiers'] = parse_notifiers_config(args.notifiers)

        if args.checks is not None:
            app.data['checks'] = parse_checks_config(args.checks)

        if args.name:
            app.name = args.name

        # TODO(dcramer): this needs to be a get_or_create pattern
        if args.repository:
            repo = Repository.query.filter(
                Repository.url == args.repository,
            ).first()
            if repo is None:
                repo = Repository(url=args.repository, vcs='git')
                db.session.add(repo)
                db.session.flush()
            app.repository_id = repo.id

        db.session.add(app)
        db.session.commit()

        context = serialize(app)
        context.update({
            'provider': app.provider,
            'provider_config': app.provider_config,
            'notifiers': app.notifiers,
            'checks': app.checks,
        })

        return self.respond(context)

    def delete(self, app_id):
        """
        Delete an app.
        """
        app = App.query.get(app_id)
        if app is None:
            return self.error('Invalid app', name='invalid_resource', status_code=404)

        celery.send_task("freight.delete_object", kwargs={'model': 'App', 'app_id': app.id})

        return self.respond({"id": str(app.id)})
