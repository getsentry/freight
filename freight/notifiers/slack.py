from __future__ import absolute_import

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

    def send_deploy(self, deploy, task, config, event):
        webhook_url = config['webhook_url']

        app = App.query.get(deploy.app_id)

        params = {
            'number': deploy.number,
            'app_name': app.name,
            'params': dict(task.params or {}),
            'env': deploy.environment,
            'ref': task.ref,
            'sha': task.sha[:7] if task.sha else task.ref,
            'status_label': task.status_label,
            'duration': task.duration,
            'link': http.absolute_uri('/deploys/{}/{}/{}'.format(app.name, deploy.environment, deploy.number)),
        }

        # TODO(dcramer): show the ref when it differs from the sha
        if event == NotifierEvent.TASK_QUEUED:
            title = "[{app_name}/{env}] Queued deploy <{link}|#{number}> ({sha})".format(**params)
        elif event == NotifierEvent.TASK_STARTED:
            title = "[{app_name}/{env}] Starting deploy <{link}|#{number}> ({sha})".format(**params)
        elif task.status == TaskStatus.failed:
            title = "[{app_name}/{env}] Failed to deploy <{link}|#{number}> ({sha}) after {duration}s".format(**params)
        elif task.status == TaskStatus.cancelled:
            title = "[{app_name}/{env}] Deploy <{link}|#{number}> ({sha}) was cancelled after {duration}s".format(**params)
        elif task.status == TaskStatus.finished:
            title = "[{app_name}/{env}] Successfully deployed <{link}|#{number}> ({sha}) after {duration}s".format(**params)
        else:
            raise NotImplementedError(task.status)

        payload = {
            'parse': 'none',
            'text': title,
        }

        values = {'payload': json.dumps(payload)}

        http.post(webhook_url, values)
