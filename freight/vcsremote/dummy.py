from .base import VcsRemote


class DummyVcsRemote(VcsRemote):
    hostname = "example.com"

    @property
    def repo_url(self) -> str:
        return ""

    def get_commit_url(self, sha: str) -> str:
        return ""
