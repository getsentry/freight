from __future__ import absolute_import, unicode_literals

__all__ = ['SlackNotifier']

import json
import requests

from ds.models import TaskStatus

from .base import Notifier


class SlackNotifier(Notifier):
    def get_options(self):
        return {
            'webhook_url': {'required': True},
        }

    def color_for_status(self, status):
        if status == TaskStatus.failed:
            return '#d20f2a'
        return '#2788ce'

    def send(self, task, config):
        webhook_url = config['webhook_url']

        title = "Task '{task_name}' of '{ref}' {status_label}".format(
            task_name=task.name,
            ref=task.ref,
            status_label=task.status_label
        )

        payload = {
            'parse': 'none',
            'text': title,
            'attachments': [{
                'color': self.color_for_status(task.status),
                'fields': [{
                    'title': 'Details',
                    'value': 'Sha: {sha}\nEnv: {env}'.format(
                        sha=task.sha,
                        env=task.environment,
                    ),
                    'short': False,
                }]
            }]
        }

        values = {'payload': json.dumps(payload)}

        requests.post(webhook_url, values)
