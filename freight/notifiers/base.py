from __future__ import absolute_import

from freight.models import Deploy

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
