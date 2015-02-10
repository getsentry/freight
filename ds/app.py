"""
This file acts as a default entry point for app creation.
"""
from __future__ import absolute_import

from ds.config import create_app, celery  # NOQA


def patch_celery(app):
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask


app = create_app()
patch_celery(app)
