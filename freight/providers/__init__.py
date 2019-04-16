from .manager import ProviderManager
from .shell import ShellProvider

manager = ProviderManager()
manager.add("shell", ShellProvider)

get = manager.get
