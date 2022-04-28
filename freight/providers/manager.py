__all__ = ["ProviderManager"]

from freight.exceptions import InvalidProvider


class ProviderManager:
    def __init__(self):
        self.providers = {}

    def add(self, name, cls):
        self.providers[name] = cls

    def get(self, name, **kwargs):
        try:
            cls = self.providers[name]
        except KeyError:
            raise InvalidProvider(name)
        return cls(**kwargs)
