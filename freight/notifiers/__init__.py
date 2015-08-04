from __future__ import absolute_import

from .base import Notifier, NotifierEvent  # NOQA
from .dummy import DummyNotifier
from .manager import NotifierManager
from .sentry import SentryNotifier
from .slack import SlackNotifier
from .queue import NotificationQueue

queue = NotificationQueue()

manager = NotifierManager()
manager.add('dummy', DummyNotifier)
manager.add('sentry', SentryNotifier)
manager.add('slack', SlackNotifier)

get = manager.get
