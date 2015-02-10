from __future__ import absolute_import

import celery

from celery import signals


class ContextualCelery(celery.Celery):
    def __init__(self, *args, **kwargs):
        super(ContextualCelery, self).__init__(*args, **kwargs)

    def on_task_prerun(self, *args, **kwargs):
        ctx = self.__flask_app.app_context()
        ctx.push()
        self.__flask_context.append(ctx)

    def on_task_postrun(self, *args, **kwargs):
        ctx = self.__flask_context.pop()
        self.__sqla_db.session.commit()
        self.__sqla_db.session.remove()
        ctx.pop()

    def init_app(self, app, db):
        self.__flask_context = []
        self.__flask_app = app
        self.__sqla_db = db
        self.conf.update(app.config)
        signals.task_prerun.connect(self.on_task_prerun)
        signals.task_postrun.connect(self.on_task_postrun)
