__all__ = ["HooksManager"]

from freight.exceptions import InvalidHook


class HooksManager(object):
    def __init__(self):
        self._register = {}

    def add(self, name, cls):
        self._register[name] = cls

    def get(self, name, **kwargs):
        try:
            cls = self._register[name]
        except KeyError:
            raise InvalidHook(name)
        return cls(**kwargs)
