from __future__ import absolute_import

import flask
import os
import logging

from celery import Celery
from flask import current_app
from flask_heroku import Heroku
from flask_redis import Redis
from flask_sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

from ds.api.controller import ApiController
from ds.constants import PROJECT_ROOT


api = ApiController(prefix='/api/0')
db = SQLAlchemy(session_options={})
celery = Celery()
heroku = Heroku()
redis = Redis()
sentry = Sentry(logging=True, level=logging.WARN)


def patch_celery():
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with current_app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask

patch_celery()


def create_app(_read_config=True, **config):
    from kombu import Queue

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

    app.config['WORKSPACE_ROOT'] = os.environ.get('WORKSPACE_ROOT', '/tmp')

    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_POOL_SIZE'] = 60
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20

    app.config['BROKER_TRANSPORT'] = None

    app.config['CELERY_ACCEPT_CONTENT'] = ['json']
    app.config['CELERY_ACKS_LATE'] = True
    app.config['CELERY_DEFAULT_QUEUE'] = "default"
    app.config['CELERY_DEFAULT_EXCHANGE'] = "default"
    app.config['CELERY_DEFAULT_EXCHANGE_TYPE'] = "direct"
    app.config['CELERY_DEFAULT_ROUTING_KEY'] = "default"
    app.config['CELERY_DISABLE_RATE_LIMITS'] = True
    app.config['CELERY_IGNORE_RESULT'] = True
    app.config['CELERY_RESULT_BACKEND'] = None
    app.config['CELERY_RESULT_SERIALIZER'] = 'json'
    app.config['CELERY_SEND_EVENTS'] = False
    app.config['CELERY_TASK_RESULT_EXPIRES'] = 1
    app.config['CELERY_TASK_SERIALIZER'] = 'json'
    app.config['CELERY_TIMEZONE'] = 'UTC'
    app.config['CELERYD_PREFETCH_MULTIPLIER'] = 1
    app.config['CELERYD_MAX_TASKS_PER_CHILD'] = 10000

    app.config['CELERY_QUEUES'] = (
        Queue('default', routing_key='default'),
        Queue('ds.tasks', routing_key='ds.tasks'),
    )

    app.config['CELERY_IMPORTS'] = (
        'ds.tasks',
    )

    app.config['CELERY_ROUTES'] = {
        'ds.execute_task': {
            'queue': 'ds.tasks',
            'routing_key': 'ds.tasks',
        },
    }

    app.config['SENTRY_INCLUDE_PATHS'] = [
        'ds',
    ]

    # Pull in Heroku configuration
    heroku.init_app(app)

    # Set any remaining defaults that might not be present yet
    if not app.config.get('SQLALCHEMY_DATABASE_URI'):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ds'

    if not app.config.get('BROKER_URL'):
        app.config['BROKER_URL'] = 'redis://localhost/0'

    app.config.update(config)

    if _read_config:
        if os.environ.get('DS_CONF'):
            # DS_CONF=/etc/ds.conf.py
            app.config.from_envvar('DS_CONF')
        else:
            # Look for ~/.ds/ds.conf.py
            path = os.path.normpath(os.path.expanduser('~/.ds/ds.conf.py'))
            app.config.from_pyfile(path, silent=True)

    configure_sentry(app)
    configure_api(app)
    configure_celery(app)
    configure_redis(app)
    configure_sqlalchemy(app)

    return app


def configure_api(app):
    from ds.api.controller import ApiCatchall
    from ds.api.app_details import AppDetailsApiView
    from ds.api.app_index import AppIndexApiView
    from ds.api.task_index import TaskIndexApiView

    api.add_resource(AppDetailsApiView, '/apps/<app_id>/')
    api.add_resource(AppIndexApiView, '/apps/')
    api.add_resource(TaskIndexApiView, '/tasks/')
    # catchall should be the last resource
    api.add_resource(ApiCatchall, '/<path:path>')
    # init must be called after routes are registered
    api.init_app(app)


def configure_celery(app):
    from celery.signals import task_postrun

    celery.conf.update(app.config)

    @task_postrun.connect
    def cleanup_session(*args, **kwargs):
        """
        Emulate a request cycle for each task to ensure the session objects
        get cleaned up as expected.
        """
        db.session.commit()
        db.session.remove()


def configure_redis(app):
    redis.init_app(app)


def configure_sentry(app):
    from raven.contrib.celery import register_signal, register_logger_signal

    sentry.init_app(app)

    register_signal(sentry.client)
    register_logger_signal(sentry.client)


def configure_sqlalchemy(app):
    db.init_app(app)
