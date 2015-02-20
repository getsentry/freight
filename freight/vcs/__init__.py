from __future__ import absolute_import, unicode_literals

from .base import UnknownRevision  # NOQA
from .manager import VcsManager
from .git import GitVcs

manager = VcsManager()
manager.add('git', GitVcs)

get = manager.get
