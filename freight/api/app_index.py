from __future__ import absolute_import, unicode_literals

import json

from flask_restful import reqparse

from freight.api.base import ApiView
from freight.api.serializer import serialize
from freight.checks.utils import parse_checks_config
from freight.config import db
from freight.models import App, Repository
from freight.notifiers.utils import parse_notifiers_config
from freight.providers.utils import parse_provider_config


class AppIndexApiView(ApiView):
    get_parser = reqparse.RequestParser()
    get_parser.add_argument('name', location='args')

    def get(self):
        """
        Retrieve a list of apps.
        """
        args = self.get_parser.parse_args()

        qs_filters = []

        if args.name:
            qs_filters.append(App.name == args.name)

        app_qs = App.query.filter(*qs_filters).order_by(App.id.desc())

        return self.paginate(app_qs, on_results=serialize)

    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name', required=True)
    post_parser.add_argument('repository', required=True)
    post_parser.add_argument('provider', required=True)
    post_parser.add_argument('provider_config', type=json.loads)
    post_parser.add_argument('notifiers', type=json.loads)
    post_parser.add_argument('checks', type=json.loads)

    def post(self):
        """
        Create a new app.
        """
        args = self.post_parser.parse_args()

        provider_config = parse_provider_config(args.provider, args.provider_config or {})

        checks_config = parse_checks_config(args.checks or [])

        notifiers_config = parse_notifiers_config(args.notifiers or [])

        # TODO(dcramer): this needs to be a get_or_create pattern
        repo = Repository.query.filter(
            Repository.url == args.repository,
        ).first()
        if repo is None:
            repo = Repository(url=args.repository, vcs='git')
            db.session.add(repo)
            db.session.flush()

        app = App(
            name=args.name,
            repository_id=repo.id,
            provider=args.provider,
            data={
                'provider_config': provider_config,
                'notifiers': notifiers_config,
                'checks': checks_config,
            },
        )
        db.session.add(app)
        db.session.commit()

        return self.respond(serialize(app), status_code=201)
