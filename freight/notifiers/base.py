from __future__ import absolute_import

from freight.models import Deploy, TaskStatus

__all__ = ['Notifier', 'NotifierEvent']


class NotifierEvent(object):
    TASK_STARTED = 0
    TASK_FINISHED = 1
    TASK_QUEUED = 2


class Notifier(object):
    DEFAULT_EVENTS = [
        NotifierEvent.TASK_QUEUED,
        NotifierEvent.TASK_STARTED,
        NotifierEvent.TASK_FINISHED,
    ]

    def get_default_options(self):
        return {
            # TODO(dcramer): we want to support events, but we need validators
            # before that can happen to avoid magical constants
            # 'events': {},
        }

    def get_options(self):
        return {}

    def send(self, task, config, event):
        # TODO(mattrobenolt): Split this out into send_deploy, send_x
        # since we want different notifications for different tasks,
        # and remove this shim. For now, we there are only deploys
        deploy = Deploy.query.filter(Deploy.task_id == task.id).first()
        return self.send_deploy(deploy, task, config, event)

    def send_deploy(self, deploy, task, config, event):
        raise NotImplementedError

    def should_send(self, task, config, event):
        deploy = Deploy.query.filter(Deploy.task_id == task.id).first()
        return self.should_send_deploy(deploy, task, config, event)

    def should_send_deploy(self, deploy, task, config, event):
        return event in config.get('events', self.DEFAULT_EVENTS)


def format_link(link, deploy, notifier):
    if notifier == 'datadog':
        return '{link}'                        # datadog parses the text and auto-generates links
    else:
        return '<{link}|#{deploy.number}>'     # default to slack style formatting


def generate_event_title(app, deploy, task, user, event, link):
    params = {
        'number': deploy.number,
        'app_name': app.name,
        'params': dict(task.params or {}),
        'env': deploy.environment,
        'ref': task.ref,
        'sha': task.sha[:7] if task.sha else task.ref,
        'status_label': task.status_label,
        'duration': task.duration,
        'user': user.name.split('@', 1)[0],  # Usernames can either be 'user' or 'user@example.com',
        'display_link': link
    }

    # TODO(dcramer): show the ref when it differs from the sha
    if event == NotifierEvent.TASK_QUEUED:
        return "[{app_name}/{env}] {user} queued deploy {display_link} ({sha})".format(**params)
    if event == NotifierEvent.TASK_STARTED:
        return "[{app_name}/{env}] {user} started deploy {display_link} ({sha})".format(**params)
    if task.status == TaskStatus.failed:
        return "[{app_name}/{env}] Failed to finish {user}'s deploy {display_link} ({sha}) after {duration}s".format(**params)
    if task.status == TaskStatus.cancelled:
        return "[{app_name}/{env}] {user}'s deploy {display_link} ({sha}) was cancelled after {duration}s".format(**params)
    if task.status == TaskStatus.finished:
        return "[{app_name}/{env}] Successfully finished {user}'s deploy {display_link} ({sha}) after {duration}s".format(**params)
    raise NotImplementedError(task.status)
