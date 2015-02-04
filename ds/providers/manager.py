from __future__ import absolute_import

__all__ = ['ProviderManager']


class ProviderManager(object):
    def __init__(self):
        self.providers = {}

    def add(self, name, cls):
        self.providers[name] = cls

    def get(self, name, **kwargs):
        return self.providers.get(name)(**kwargs)
