from .manager import ProviderManager
from .pipeline import PipelineProvider
from .shell import ShellProvider

manager = ProviderManager()
manager.add("pipeline", PipelineProvider)
manager.add("shell", ShellProvider)

get = manager.get
