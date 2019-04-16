__all__ = ["SlackNotifier"]

import json

from freight import http
from freight.models import App, Task, User

from .base import Notifier, generate_event_title


class SlackNotifier(Notifier):
    def get_options(self):
        return {"webhook_url": {"required": True}}

    def send_deploy(self, deploy, task, config, event):
        webhook_url = config["webhook_url"]

        app = App.query.get(deploy.app_id)
        task = Task.query.get(deploy.task_id)
        user = User.query.get(task.user_id)
        title = generate_event_title(app, deploy, task, user, event)

        payload = {"parse": "none", "text": title}

        values = {"payload": json.dumps(payload)}

        http.post(webhook_url, values)
