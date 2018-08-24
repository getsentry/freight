from __future__ import absolute_import

from .manager import ProviderManager
from .shell import ShellProvider
from .craft import CraftProvider

manager = ProviderManager()
manager.add('shell', ShellProvider)
manager.add('craft', CraftProvider)

get = manager.get
