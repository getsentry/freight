from __future__ import absolute_import, unicode_literals

import json

from flask_restful import reqparse
from itertools import chain

from ds import notifiers, providers
from ds.api.base import ApiView
from ds.api.serializer import serialize
from ds.config import celery, db
from ds.exceptions import InvalidNotifier, InvalidProvider
from ds.models import App, Repository


class AppDetailsApiView(ApiView):
    put_parser = reqparse.RequestParser()
    put_parser.add_argument('name')
    put_parser.add_argument('repository')
    put_parser.add_argument('provider')
    put_parser.add_argument('provider_config', type=json.loads)
    put_parser.add_argument('notifiers', type=json.loads)

    def put(self, app_id):
        """
        Update an app.
        """
        args = self.put_parser.parse_args()

        app = App.query.get(app_id)
        if app is None:
            return self.error('Invalid app', name='invalid_resource', status_code=404)

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
            all_options = chain(provider.get_default_options().items(),
                                provider.get_options().items())
            for option, option_values in all_options:
                value = cur_provider_config.get(option)
                if option_values.get('required') and not value:
                    return self.error(
                        message='Missing required provider option: %s' % (option,),
                        name='invalid_provider_config',
                    )
                new_provider_config[option] = value
            app.data['provider_config'] = new_provider_config

        if args.notifiers is not None:
            new_notifiers = []
            for data in args.notifiers:
                try:
                    notifier = notifiers.get(data['type'])
                except InvalidNotifier:
                    return self.error('Invalid notifier: {}'.format(data['type']),
                                      name='invalid_notifier')

                config = data.get('config', {})
                all_options = chain(notifier.get_default_options().items(),
                                    notifier.get_options().items())
                for option, option_values in all_options:
                    value = config.get(option)
                    if option_values.get('required') and not value:
                        return self.error(
                            message='Missing required notifier option: %s' % (option,),
                            name='invalid_notifier_config',
                        )
                    new_notifiers.append({'type': data['type'], 'config': config})
            app.data['notifiers'] = new_notifiers

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
        })

        return self.respond(context)

    def delete(self, app_id):
        """
        Delete an app.
        """
        app = App.query.get(app_id)
        if app is None:
            return self.error('Invalid app', name='invalid_resource', status_code=404)

        celery.send_task("ds.delete_object", kwargs={'model': 'App', 'app_id': app.id})

        return self.respond({"id": str(app.id)})
