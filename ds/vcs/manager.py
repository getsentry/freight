from __future__ import absolute_import, unicode_literals

__all__ = ['VcsManager']


class VcsManager(object):
    def __init__(self):
        self.backends = {}

    def add(self, name, cls):
        self.backends[name] = cls

    def get(self, name, **kwargs):
        return self.backends.get(name)(**kwargs)
