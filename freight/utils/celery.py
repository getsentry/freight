from __future__ import absolute_import, unicode_literals

import celery

from celery import signals


class ContextualCelery(celery.Celery):
    def on_task_prerun(self, *args, **kwargs):
        ctx = self.__flask_app.app_context()
        ctx.push()
        self.__flask_context.append(ctx)

    def on_task_postrun(self, *args, **kwargs):
        ctx = self.__flask_context.pop()
        ctx.pop()

    def init_app(self, app):
        self.__flask_context = []
        self.__flask_app = app
        self.conf.update(app.config)
        signals.task_prerun.connect(self.on_task_prerun)
        signals.task_postrun.connect(self.on_task_postrun)

    def apply(self, name, *args, **kwargs):
        return self.tasks[name](*args, **kwargs)

    def task(self, *args, **kwargs):
        from freight.tasks.base import ExtendedTask
        kwargs.setdefault('base', ExtendedTask)
        return super(ContextualCelery, self).task(*args, **kwargs)
