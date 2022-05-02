__all__ = ["VcsManager"]


class VcsManager:
    def __init__(self):
        self.backends = {}

    def add(self, name, cls):
        self.backends[name] = cls

    def get(self, name, **kwargs):
        return self.backends.get(name)(**kwargs)
