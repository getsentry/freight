from __future__ import absolute_import

from .base import Notifier, NotifierEvent  # NOQA
from .dummy import DummyNotifier
from .datadog import DatadogNotifier
from .manager import NotifierManager
from .sentry import SentryNotifier
from .slack import SlackNotifier
from .github import GithubNotifier
from .queue import NotificationQueue

queue = NotificationQueue()

manager = NotifierManager()
manager.add('dummy', DummyNotifier)
manager.add('datadog', DatadogNotifier)
manager.add('sentry', SentryNotifier)
manager.add('slack', SlackNotifier)
manager.add('github', GithubNotifier)

get = manager.get
