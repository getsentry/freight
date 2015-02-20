from __future__ import absolute_import, unicode_literals

__all__ = ['NotifierManager']

from freight.exceptions import InvalidNotifier


class NotifierManager(object):
    def __init__(self):
        self.notifiers = {}

    def add(self, name, cls):
        self.notifiers[name] = cls

    def get(self, name, **kwargs):
        try:
            cls = self.notifiers[name]
        except KeyError:
            raise InvalidNotifier(name)
        return cls(**kwargs)
