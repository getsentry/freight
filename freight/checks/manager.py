__all__ = ["CheckManager"]

from freight.exceptions import InvalidCheck


class CheckManager:
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
