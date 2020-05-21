from .base import Notifier, NotifierEvent  # NOQA
from .datadog import DatadogNotifier
from .dummy import DummyNotifier
from .generic import GenericNotifier
from .github import GithubNotifier
from .manager import NotifierManager
from .queue import NotificationQueue
from .sentry import SentryNotifier
from .slack import SlackNotifier

queue = NotificationQueue()

manager = NotifierManager()
manager.add("datadog", DatadogNotifier)
manager.add("dummy", DummyNotifier)
manager.add("generic", GenericNotifier)
manager.add("github", GithubNotifier)
manager.add("sentry", SentryNotifier)
manager.add("slack", SlackNotifier)

get = manager.get
