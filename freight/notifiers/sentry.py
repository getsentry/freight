from __future__ import absolute_import

__all__ = ['SentryNotifier']

from freight import http
from freight.models import App, TaskStatus

from .base import Notifier, NotifierEvent


class SentryNotifier(Notifier):
    def get_options(self):
        return {
            'webhook_url': {'required': True},
        }

    def send(self, task, config, event):
        if task.status != TaskStatus.finished and event != NotifierEvent.TASK_STARTED:
            return

        webhook_url = config['webhook_url']

        app = App.query.get(task.app_id)

        payload = {
            'number': task.number,
            'app_name': app.name,
            'task_name': task.name,
            'env': task.environment,
            'ref': task.ref,
            'sha': task.sha,
            'duration': task.duration,
            'event': 'started' if event == NotifierEvent.TASK_STARTED else 'finished',
            'dateStarted': task.date_started.isoformat() + 'Z' if task.date_started else None,
            'dateFinished': task.date_finished.isoformat() + 'Z' if task.date_finished else None,
            'link': http.absolute_uri('/tasks/{}/'.format(task.id)),
        }

        http.post(webhook_url, json=payload)
