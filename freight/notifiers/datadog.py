from __future__ import absolute_import

__all__ = ['DatadogNotifier']

from freight import http
from freight.models import App, TaskStatus

from .base import Notifier, NotifierEvent


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

# https://docs.datadoghq.com/api/?lang=bash#post-an-event
# This provides a bunch of tags to refine searches in datadog, as well as a title for the deployment
    def send_deploy(self, deploy, task, config, event):
        webhook_url = config['webhook_url']

        app = App.query.get(deploy.app_id)

        payload = {
            'title': "[{app_name}/{env}] deployed by {user}".format(**params)
            'text': "[{app_name}/{env}] {user} deployed <{link}|#{number}> ({sha})".format(**params)
            'priority': "normal",
            'alert_type': "info",
            'tags': [{
                'number': deploy.number,
                'freight_deploy_name': app.name + "/" + deploy.environment + "#" + deploy.number,
                'freight_deploy_status': event,
                'freight_app': app.name,
                'freight_ref': task.ref,
                'freight_sha': task.sha,
                'freight_deploy_duration': task.duration,
                'freight_event': 'started' if event == NotifierEvent.TASK_STARTED else 'finished',
                'freight_deploy_dateStarted': task.date_started.isoformat() + 'Z' if task.date_started else None,
                'dateReleased': task.date_finished.isoformat() + 'Z' if task.date_finished else None,
                'link': http.absolute_uri('/deploys/{}/{}/{}/'.format(app.name, deploy.environment, deploy.number))
            }]
        }

        http.post(webhook_url, json=payload)
