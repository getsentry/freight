from __future__ import absolute_import

from .base import Check  # NOQA
from .manager import CheckManager
from .github import GitHubContextCheck
from .build import BuildStatusCheck

manager = CheckManager()
manager.add('github', GitHubContextCheck)
manager.add('build', BuildStatusCheck)

get = manager.get
