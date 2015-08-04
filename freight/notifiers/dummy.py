from __future__ import absolute_import

__all__ = ['DummyNotifier']

from .base import Notifier


class DummyNotifier(Notifier):
    def get_options(self):
        return {}

    def send(self, task, config, event):
        return
