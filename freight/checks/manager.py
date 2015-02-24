from __future__ import absolute_import, unicode_literals

__all__ = ['CheckManager']

from freight.exceptions import InvalidCheck


class CheckManager(object):
    def __init__(self):
        self._register = {}

    def add(self, name, cls):
        self._register[name] = cls

    def get(self, name, **kwargs):
        try:
            cls = self._register[name]
        except KeyError:
            raise InvalidCheck(name)
        return cls(**kwargs)
