from .manager import ProviderManager
from .kubernetes import KubernetesProvider
from .shell import ShellProvider

manager = ProviderManager()
manager.add("kubernetes", KubernetesProvider)
manager.add("shell", ShellProvider)

get = manager.get
