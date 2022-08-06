from typing import List


class VcsRemote:
    hostname: str
    """
    The hostname of the remote. Used by the VcsRemoteManager to map a VCS
    remote URL to a VcsRemote.
    """

    def __init__(self, repo):
        self.repo = repo

    @property
    def repo_url(self) -> str:
        """
        Get's the base URL for the remote repository
        """
        raise NotImplementedError

    def get_commit_url(self, commit: str) -> str:
        """
        Get the URL for a particular commit on the remote
        """
        raise NotImplementedError

    def get_commits_info(self, shas: List[str]):
        """
        Retrieves detailed information from the remote for a list of commits.
        """
        raise NotImplementedError

    def get_sha_range(self, ref1, ref2):
        """
        Given two refs, returna list of SHAs between and including the refs.
        """
        raise NotImplementedError
