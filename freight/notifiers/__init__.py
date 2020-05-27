from .base import Notifier, NotifierEvent  # NOQA
from .datadog import DatadogNotifier
from .dummy import DummyNotifier
from .webhook import WebhookNotifier
from .github import GithubNotifier
from .manager import NotifierManager
from .queue import NotificationQueue
from .sentry import SentryNotifier
from .slack import SlackNotifier

queue = NotificationQueue()

manager = NotifierManager()
manager.add("datadog", DatadogNotifier)
manager.add("dummy", DummyNotifier)
manager.add("webhook", WebhookNotifier)
manager.add("github", GithubNotifier)
manager.add("sentry", SentryNotifier)
manager.add("slack", SlackNotifier)

get = manager.get
