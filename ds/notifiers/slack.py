from __future__ import absolute_import, unicode_literals

__all__ = ['SlackNotifier']

import json
import requests

from ds.models import App, TaskStatus

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
            title = "Deploying {app_name}#{number} ({ref}) to {env}".format(**params)
        elif task.status == TaskStatus.failed:
            title = "Failed to deploy {app_name}#{number} to {env} ({duration}s)".format(**params)
        elif task.status == TaskStatus.finished:
            title = "Successfully deployed {app_name}#{number} ({sha}) to {env} ({duration}s)".format(**params)
        else:
            raise NotImplementedError(task.status)

        payload = {
            'parse': 'none',
            'text': title,
        }

        values = {'payload': json.dumps(payload)}

        requests.post(webhook_url, values)
