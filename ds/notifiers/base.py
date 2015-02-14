from __future__ import absolute_import, unicode_literals

__all__ = ['Notifier']


class Notifier(object):
    def get_options(self):
        return {}

    def send(self, task, config):
        raise NotImplementedError
