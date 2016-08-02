from __future__ import absolute_import

__all__ = ['GithubNotifier']

from flask import current_app

from freight import http
from freight.models import App, Task, TaskStatus

from .base import Notifier, NotifierEvent


class GithubNotifier(Notifier):
    def get_options(self):
        return {
            'repo': {'required': True},
            'api_root': {'required': False},
        }

    def send_deploy(self, deploy, task, config, event):
        token = current_app.config['GITHUB_TOKEN']
        if not token:
            raise ValueError('GITHUB_TOKEN is not set')
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': 'token {}'.format(token),
        }

        app = App.query.get(deploy.app_id)
        task = Task.query.get(deploy.task_id)

        api_root = (
            config.get('api_root') or current_app.config['GITHUB_API_ROOT']
        ).rstrip('/')

        url = '{api_root}/repos/{repo}/statuses/{sha}'.format(
            api_root=api_root,
            repo=config['repo'],
            sha=task.sha,
        )

        target_url = http.absolute_uri('/deploys/{}/{}/{}'.format(
            app.name,
            deploy.environment,
            deploy.number
        ))

        if event == NotifierEvent.TASK_QUEUED:
            state = 'pending'
            description = 'The freight deploy is current queued.'
        elif event == NotifierEvent.TASK_STARTED:
            state = 'pending'
            description = 'The freight deploy has started.'
        elif task.status == TaskStatus.failed:
            state = 'failure'
            description = 'The freight deploy has failed.'
        elif task.status == TaskStatus.cancelled:
            state = 'error'
            description = 'The freight deploy has been cancelled.'
        elif task.status == TaskStatus.finished:
            state = 'success'
            description = 'The freight deploy has finished successfully.'
        else:
            raise NotImplementedError(task.status)

        payload = {
            'state': state,
            'target_url': target_url,
            'description': description,
            'context': 'continuous-integration/freight/deploy',
        }

        http.post(url, headers=headers, json=payload)
