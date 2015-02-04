from __future__ import absolute_import

import flask
import os
import logging

from celery import Celery
from flask import current_app
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry

from ds.constants import PROJECT_ROOT


db = SQLAlchemy(session_options={})
celery = Celery()
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

    # This key is insecure and you should override it on the server
    app.config['SECRET_KEY'] = 't\xad\xe7\xff%\xd2.\xfe\x03\x02=\xec\xaf\\2+\xb8=\xf7\x8a\x9aLD\xb1'

    app.config['REPO_ROOT'] = '/tmp/ds-workspace/repos'

    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///ds'
    app.config['SQLALCHEMY_POOL_SIZE'] = 60
    app.config['SQLALCHEMY_MAX_OVERFLOW'] = 20

    app.config['CELERY_ACCEPT_CONTENT'] = ['json']
    app.config['CELERY_ACKS_LATE'] = True
    app.config['CELERY_BROKER_URL'] = 'redis://localhost/0'
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

    app.config['SENTRY_DSN'] = None
    app.config['SENTRY_INCLUDE_PATHS'] = [
        'ds',
    ]

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
    configure_celery(app)
    configure_sqlalchemy(app)

    return app


def configure_celery(app):
    from celery.signals import task_postrun

    celery.conf.update({'BROKER_URL': app.config['CELERY_BROKER_URL']})
    celery.conf.update(app.config)

    @task_postrun.connect
    def cleanup_session(*args, **kwargs):
        """
        Emulate a request cycle for each task to ensure the session objects
        get cleaned up as expected.
        """
        db.session.commit()
        db.session.remove()


def configure_sentry(app):
    from raven.contrib.celery import register_signal, register_logger_signal

    sentry.init_app(app)

    register_signal(sentry.client)
    register_logger_signal(sentry.client)


def configure_sqlalchemy(app):
    db.init_app(app)
