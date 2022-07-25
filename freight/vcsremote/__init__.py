from .manager import VcsRemoteManager
from .github import GitHubVcsRemote

manager = VcsRemoteManager()
manager.add("github", GitHubVcsRemote)

get = manager.get
get_by_repo = manager.get_by_repo
