from __future__ import absolute_import, unicode_literals

__all__ = ['Notifier', 'NotifierEvent']


class NotifierEvent(object):
    TASK_STARTED = 0
    TASK_FINISHED = 1


class Notifier(object):
    DEFAULT_EVENTS = [NotifierEvent.TASK_STARTED, NotifierEvent.TASK_FINISHED]

    def get_default_options(self):
        return {
            # TODO(dcramer): we want to support events, but we need validators
            # before that can happen to avoid magical constants
            # 'events': {},
        }

    def get_options(self):
        return {}

    def send(self, task, config, event):
        raise NotImplementedError

    def should_send(self, task, config, event):
        return event in config.get('events', self.DEFAULT_EVENTS)
