from __future__ import absolute_import

from .manager import HooksManager
from .github import GitHubHooks

manager = HooksManager()
manager.add('github', GitHubHooks)

get = manager.get
