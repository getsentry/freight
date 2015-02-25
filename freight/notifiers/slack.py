from __future__ import absolute_import, unicode_literals

__all__ = ['SlackNotifier']

import json

from freight import http
from freight.models import App, TaskStatus

from .base import Notifier, NotifierEvent


class SlackNotifier(Notifier):
    def get_options(self):
        return {
            'webhook_url': {'required': True},
        }

    def send(self, task, config, event):
        webhook_url = config['webhook_url']

        app = App.query.get(task.app_id)

        params = {
            'number': task.number,
            'app_name': app.name,
            'task_name': task.name,
            'env': task.environment,
            'ref': task.ref,
            'sha': task.sha[:7] if task.sha else task.ref,
            'status_label': task.status_label,
            'duration': task.duration,
        }

        if event == NotifierEvent.TASK_STARTED:
            title = "[{app_name}/{env}] Starting deploy #{number} ({sha})".format(**params)
        elif task.status == TaskStatus.failed:
            title = "[{app_name}/{env}] Failed to deploy {sha} after {duration}s".format(**params)
        elif task.status == TaskStatus.cancelled:
            title = "[{app_name}/{env}] Deploy of {sha} was cancelled after {duration}s".format(**params)
        elif task.status == TaskStatus.finished:
            title = "[{app_name}/{env}] Successfully deployed #{number} ({sha}) after {duration}s".format(**params)
        else:
            raise NotImplementedError(task.status)

        payload = {
            'parse': 'none',
            'text': title,
        }

        values = {'payload': json.dumps(payload)}

        http.post(webhook_url, values)
