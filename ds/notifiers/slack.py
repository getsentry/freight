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

    def color_for_status(self, status):
        if status == TaskStatus.failed:
            return '#d20f2a'
        return '#2788ce'

    def send(self, task, config, event):
        webhook_url = config['webhook_url']

        app = App.query.get(task.app_id)

        params = {
            'app_name': app.name,
            'task_name': task.name,
            'env': task.environment,
            'sha': task.sha[:12],
            'ref': task.ref,
            'status_label': task.status_label,
            'duration': task.duration,
        }

        if event == NotifierEvent.TASK_STARTED:
            title = "[{app_name}] Executing '{task_name}' of {ref} ({sha}) on {env}".format(**params)
        else:
            title = "[{app_name}] '{task_name}' on {env} {status_label} (took {duration}s)".format(**params)

        payload = {
            'parse': 'none',
            'text': title,
        }

        values = {'payload': json.dumps(payload)}

        requests.post(webhook_url, values)
