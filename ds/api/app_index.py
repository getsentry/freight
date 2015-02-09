from __future__ import absolute_import

import json

from flask_restful import reqparse

from ds import providers
from ds.api.base import ApiView
from ds.api.serializer import serialize
from ds.config import db
from ds.exceptions import InvalidProvider
from ds.models import App, Repository


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
    post_parser.add_argument('provider_config', default='{}', type=json.loads)

    def post(self):
        """
        Create a new app.
        """
        args = self.post_parser.parse_args()

        try:
            provider = providers.get(args.provider)
        except InvalidProvider:
            return self.error('Invalid provider', name='invalid_provider')

        provider_config = {}
        for option, option_values in provider.get_options().items():
            value = args.provider_config.get(option)
            if option_values.get('required') and not value:
                return self.error(
                    message='Missing required provider option: %s' % (option,),
                    name='invalid_provider_config',
                )
            provider_config[option] = value

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
            data={'provider_config': provider_config},
        )
        db.session.add(app)
        db.session.commit()

        return self.respond(serialize(app), status_code=201)
