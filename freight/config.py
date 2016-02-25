from __future__ import absolute_import

import flask
import os
import logging
from urlparse import urlunsplit

from flask_heroku import Heroku
from flask_redis import Redis
from flask_sslify import SSLify
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

from freight.queue import Queue
from freight.api.controller import ApiController
from freight.constants import PROJECT_ROOT


api = ApiController(prefix='/api/0')
db = SQLAlchemy(session_options={})
heroku = Heroku()
redis = Redis()
sentry = Sentry(logging=True, level=logging.WARN)
queue = Queue()


def configure_logging(app):
    logging.getLogger().setLevel(getattr(logging, app.config['LOG_LEVEL']))


def create_app(_read_config=True, **config):
    app = flask.Flask(
        __name__,
        static_folder=None,
        template_folder=os.path.join(PROJECT_ROOT, 'templates'))

    # Utilized for sessions and other secrets
    # NOTE: This key is insecure and you should override it on the server
    app.config['SECRET_KEY'] = 't\xad\xe7\xff%\xd2.\xfe\x03\x02=\xec\xaf\\2+\xb8=\xf7\x8a\x9aLD\xb1'
    if 'SECRET_KEY' in os.environ:
        app.config['SECRET_KEY'] = os.environ['SECRET_KEY']

    # The api key to authorize end users against this system.
    # NOTE: This key is insecure and you should override it on the server
    app.config['API_KEY'] = '3e84744ab2714151b1db789df82b41c0021958fe4d77406e9c0947c34f5c5a70'
    if 'API_KEY' in os.environ:
        app.config['API_KEY'] = os.environ['API_KEY']

    # The private key to use when cloning repositories
    # TODO(dcramer): this should support an on-disk option, as well as be
    # possible to override per repo
    app.config['SSH_PRIVATE_KEY'] = os.environ.get('SSH_PRIVATE_KEY', '').replace("\\n", "\n")

    app.config['FREIGHT_URL'] = os.environ.get('FREIGHT_URL', '').rstrip('/')

    if 'REDISCLOUD_URL' in os.environ:
        app.config['REDIS_URL'] = os.environ['REDISCLOUD_URL']
    elif 'REDIS_URL' in os.environ:
        app.config['REDIS_URL'] = os.environ['REDIS_URL']

    app.config['WORKSPACE_ROOT'] = os.environ.get('WORKSPACE_ROOT', '/tmp')

    app.config['DEFAULT_TIMEOUT'] = int(os.environ.get('DEFAULT_TIMEOUT', 3600))
    app.config['DEFAULT_READ_TIMEOUT'] = int(os.environ.get('DEFAULT_READ_TIMEOUT', 600))

    app.config['LOG_LEVEL'] = os.environ.get('LOG_LEVEL', 'INFO' if config.get('DEBUG') else 'ERROR')

    # Currently authentication requires Google
    app.config['GOOGLE_CLIENT_ID'] = os.environ.get('GOOGLE_CLIENT_ID')
    app.config['GOOGLE_CLIENT_SECRET'] = os.environ.get('GOOGLE_CLIENT_SECRET')
    app.config['GOOGLE_DOMAIN'] = os.environ.get('GOOGLE_DOMAIN')

    # Generate a GitHub token via Curl:
    # curlish https://api.github.com/authorizations \
    #     -u your-username \
    #     -X POST \
    #     -J scopes='repo' \
    #     -J note='freight'
    app.config['GITHUB_TOKEN'] = os.environ.get('GITHUB_TOKEN')
    app.config['GITHUB_API_ROOT'] = 'https://api.github.com'

    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_POOL_SIZE'] = 5
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 0
    if 'SQLALCHEMY_DATABASE_URI' in os.environ:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['SQLALCHEMY_DATABASE_URI']

    app.config['QUEUES'] = [
        'freight.default',
        'freight.tasks',
        'freight.queue',
        'freight.notifications',
    ]
    app.config['QUEUE_DEFAULT'] = 'freight.default'
    app.config['QUEUE_ROUTES'] = {
        'freight.jobs.execute_task': 'freight.tasks',
        'freight.jobs.check_queue': 'freight.queue',
        'freight.jobs.send_pending_notifications': 'freight.notifications',
    }
    app.config['QUEUE_SCHEDULE'] = {
        'freight.jobs.check_queue': {
            'seconds': 1,
        },
        'freight.jobs.send_pending_notifications': {
            'seconds': 1,
        },
    }

    app.config['SENTRY_INCLUDE_PATHS'] = [
        'freight',
    ]

    # We don't support non-proxied installs
    app.wsgi_app = ProxyFix(app.wsgi_app)

    # Pull in Heroku configuration
    heroku.init_app(app)

    # Pull in environment variables from docker
    docker_init_app(app)

    if 'DYNO' in os.environ:
        # XXX: the released version of flask-sslify does not support init_app
        SSLify(app)

    # Set any remaining defaults that might not be present yet
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///freight'

    app.config.setdefault('REDIS_URL', 'redis://localhost:6379')
    app.config.setdefault('REDIS_DB', 0)

    app.config.update(config)

    if _read_config:
        if os.environ.get('FREIGHT_CONF'):
            # FREIGHT_CONF=/etc/freight.conf.py
            app.config.from_envvar('FREIGHT_CONF')
        else:
            # Look for ~/.freight/freight.conf.py
            path = os.path.normpath(os.path.expanduser('~/.freight/freight.conf.py'))
            app.config.from_pyfile(path, silent=True)

    configure_logging(app)
    configure_sentry(app)
    configure_api(app)
    configure_redis(app)
    configure_queue(app)
    configure_sqlalchemy(app)
    configure_web_routes(app)

    return app


def configure_api(app):
    from freight.api.controller import ApiCatchall
    from freight.api.app_details import AppDetailsApiView
    from freight.api.app_index import AppIndexApiView
    from freight.api.stats import StatsApiView
    from freight.api.deploy_details import DeployDetailsApiView
    from freight.api.deploy_index import DeployIndexApiView
    from freight.api.deploy_log import DeployLogApiView

    api.add_resource(AppIndexApiView, '/apps/')
    api.add_resource(AppDetailsApiView, '/apps/<app>/')
    api.add_resource(StatsApiView, '/stats/')
    api.add_resource(DeployIndexApiView, '/tasks/',
                     endpoint='deploy-index-deprecated')
    api.add_resource(DeployIndexApiView, '/deploys/')

    # old style
    api.add_resource(DeployDetailsApiView, '/deploys/<deploy_id>/')
    api.add_resource(DeployLogApiView, '/deploys/<deploy_id>/log/')

    # new style
    api.add_resource(DeployDetailsApiView, '/tasks/<app>/<env>/<number>/',
                     endpoint='deploy-details-deprecated')
    api.add_resource(DeployLogApiView, '/tasks/<app>/<env>/<number>/log/',
                     endpoint='deploy-log-deprecated')
    api.add_resource(DeployDetailsApiView, '/deploys/<app>/<env>/<number>/',
                     endpoint='deploy-details')
    api.add_resource(DeployLogApiView, '/deploys/<app>/<env>/<number>/log/',
                     endpoint='deploy-log')

    # catchall should be the last resource
    api.add_resource(ApiCatchall, '/<path:path>')

    # init must be called after routes are registered
    api.init_app(app)


def configure_redis(app):
    redis.init_app(app)


def configure_queue(app):
    queue.init_app(app, db, sentry)


def configure_sentry(app):
    from flask import session

    sentry.init_app(app)

    @app.before_request
    def capture_user(*args, **kwargs):
        if 'uid' in session:
            sentry.client.user_context({
                'id': session['uid'],
                'email': session['email'],
            })


def configure_sqlalchemy(app):
    db.init_app(app)


def configure_web_routes(app):
    from freight.web.auth import AuthorizedView, LoginView, LogoutView
    from freight.web.index import IndexView
    from freight.web.static import StaticView

    static_root = os.path.join(PROJECT_ROOT, 'dist')

    app.add_url_rule(
        '/static/<path:filename>',
        view_func=StaticView.as_view(b'static', root=static_root))

    app.add_url_rule(
        '/auth/login/',
        view_func=LoginView.as_view(b'login', authorized_url='authorized'))
    app.add_url_rule(
        '/auth/logout/',
        view_func=LogoutView.as_view(b'logout', complete_url='index'))
    app.add_url_rule(
        '/auth/complete/',
        view_func=AuthorizedView.as_view(b'authorized', authorized_url='authorized', complete_url='index'))

    index_view = IndexView.as_view(b'index', login_url='login')
    app.add_url_rule('/', view_func=index_view)
    app.add_url_rule('/<path:path>', view_func=index_view)


def docker_init_app(app):
    if 'POSTGRES_PORT_5432_TCP_ADDR' in os.environ:
        scheme = 'postgresql'
        host = os.environ['POSTGRES_PORT_5432_TCP_ADDR']
        user = os.environ.get('POSTGRES_ENV_POSTGRES_USER') or 'postgres'
        password = os.environ.get('POSTGRES_ENV_POSTGRES_PASSWORD')
        db = os.environ.get('POSTGRES_ENV_POSTGRES_DB') or user
        if user and password:
            netloc = '%s:%s@%s' % (user, password, host)
        elif user:
            netloc = '%s@%s' % (user, host)
        else:
            netloc = host
        if not app.config.get('SQLALCHEMY_DATABASE_URI'):
            app.config['SQLALCHEMY_DATABASE_URI'] = urlunsplit((scheme, netloc, db, None, None))

    if 'REDIS_PORT_6379_TCP_ADDR' in os.environ:
        scheme = 'redis'
        host = os.environ['REDIS_PORT_6379_TCP_ADDR']
        port = 6379
        netloc = '%s:%d' % (host, port)
        app.config.setdefault('REDIS_URL', urlunsplit((scheme, netloc, '', None, None)))
