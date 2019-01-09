from __future__ import absolute_import

__all__ = ['DatadogNotifier']

from freight import http
from freight.models import App, Task, TaskStatus, User

from .base import Notifier, NotifierEvent, generate_event_title


class DatadogNotifier(Notifier):
    def get_options(self):
        return {
            'webhook_url': {'required': True},
        }

    def should_send_deploy(self, deploy, task, config, event):
        if event == NotifierEvent.TASK_STARTED:
            return True

        if event == NotifierEvent.TASK_FINISHED and task.status == TaskStatus.finished:
            return True

        return False

    def send_deploy(self, deploy, task, config, event):
        webhook_url = config['webhook_url']

        app = App.query.get(deploy.app_id)
        task = Task.query.get(deploy.task_id)
        user = User.query.get(task.user_id)
        title = generate_event_title(app, deploy, task, user, event)

        # https://docs.datadoghq.com/api/?lang=bash#post-an-event
        # This provides a bunch of tags to refine searches in datadog, as well as a title for the deployment
        payload = {
            'title': title,
            'text': title,
            'priority': "normal",
            'alert_type': "info",
            'tags': [
                'freight_deploy_name:' + app.name + "/" + deploy.environment + "#" + deploy.number,
                'freight_deploy_status:' + event,
                'freight_app:' +  app.name,
                'freight_ref:' + task.ref,
                'freight_sha:' + task.sha
           ]
        }

        http.post(webhook_url, json=payload)
