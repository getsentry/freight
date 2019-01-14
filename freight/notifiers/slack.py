from __future__ import absolute_import

__all__ = ['SlackNotifier']

import json

from freight import http
from freight.models import App, Task, User

from .base import Notifier, format_link, generate_event_title


class SlackNotifier(Notifier):
    def get_options(self):
        return {
            'webhook_url': {'required': True},
        }

    def send_deploy(self, deploy, task, config, event):
        webhook_url = config['webhook_url']

        app = App.query.get(deploy.app_id)
        task = Task.query.get(deploy.task_id)
        user = User.query.get(task.user_id)
        link_format = 'slack'
        link = http.absolute_uri('/deploys/{}/{}/{}'.format(app.name, deploy.environment, deploy.number))
        display_link = format_link(link, deploy.number, link_format)
        title = generate_event_title(app, deploy, task, user, event, display_link)

        payload = {
            'parse': 'none',
            'text': title,
        }

        values = {'payload': json.dumps(payload)}

        http.post(webhook_url, values)
