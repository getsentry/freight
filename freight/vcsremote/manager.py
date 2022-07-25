__all__ = ["VcsRemoteManager"]


from freight.vcsremote.base import VcsRemote
from freight.vcsremote.dummy import DummyVcsRemote


class VcsRemoteManager:
    def __init__(self):
        self.backends = {}

    def add(self, name, cls):
        self.backends[name] = cls

    def get(self, name, **kwargs) -> VcsRemote:
        return self.backends.get(name)(**kwargs)

    def get_by_repo(self, repo, **kwargs) -> VcsRemote:
        try:
            backend = next(b for b in self.backends.values() if b.hostname in repo.url)
        except StopIteration:
            return DummyVcsRemote(repo)
        return backend(repo, **kwargs)
