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
