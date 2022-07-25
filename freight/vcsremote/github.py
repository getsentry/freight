__all__ = ["GitHubVcsRemote"]

import re

from .base import VcsRemote


class GitHubVcsRemote(VcsRemote):
    hostname = "github.com"

    @property
    def repo_url(self) -> str:
        result = re.search(r"(?<=:)(?P<repo>[^\/]+\/[^.]+)", self.repo.url)

        if result is None:
            raise RuntimeError(
                "GitHub repo URL does not match expected format giithub.com:owner/repo.git"
            )

        repo = result.group("repo")
        return f"https://github.com/{repo}"

    def get_commit_url(self, sha: str) -> str:
        return f"{self.repo_url}/commit/{sha}"
