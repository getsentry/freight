from __future__ import absolute_import, unicode_literals

import json

from flask_restful import reqparse

from ds import providers
from ds.api.base import ApiView
from ds.api.serializer import serialize
from ds.config import db
from ds.exceptions import InvalidProvider
from ds.models import App, Repository


class AppDetailsApiView(ApiView):
    post_parser = reqparse.RequestParser()
    post_parser.add_argument('name')
    post_parser.add_argument('repository')
    post_parser.add_argument('provider')
    post_parser.add_argument('provider_config', type=json.loads)

    def put(self, app_id):
        """
        Update an app.
        """
        args = self.post_parser.parse_args()

        app = App.query.get(app_id)
        if app is None:
            return self.error('Invalid app', name='invalid_app')

        if args.provider:
            try:
                provider = providers.get(args.provider)
            except InvalidProvider:
                return self.error('Invalid provider', name='invalid_provider')
            app.provider = args.provider
        else:
            provider = providers.get(app.provider)

        if args.provider_config is not None or args.provider:
            if args.provider_config is not None:
                cur_provider_config = args.provider_config
            else:
                cur_provider_config = app.provider_config

            new_provider_config = {}
            for option, option_values in provider.get_options().items():
                value = cur_provider_config.get(option)
                if option_values.get('required') and not value:
                    return self.error(
                        message='Missing required provider option: %s' % (option,),
                        name='invalid_provider_config',
                    )
                new_provider_config[option] = value
            app.data['provider_config'] = new_provider_config

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

        return self.respond(serialize(app))
