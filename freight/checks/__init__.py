from .base import Check  # NOQA
from .manager import CheckManager
from .github import GitHubContextCheck
from .github_apps import GitHubAppsContextCheck
from .cloudbuilder import GCPContainerBuilderCheck

manager = CheckManager()
manager.add("github", GitHubContextCheck)
manager.add("github-apps", GitHubAppsContextCheck)
manager.add("cloudbuilder", GCPContainerBuilderCheck)

get = manager.get
