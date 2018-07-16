from __future__ import absolute_import

from .base import Check  # NOQA
from .manager import CheckManager
from .github import GitHubContextCheck
from .cloudbuilder import GCPContainerBuilderCheck

manager = CheckManager()
manager.add('github', GitHubContextCheck)
manager.add('cloudbuilder', GCPContainerBuilderCheck)

get = manager.get
