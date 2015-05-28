from __future__ import absolute_import

from .base import Notifier, NotifierEvent  # NOQA
from .manager import NotifierManager
from .sentry import SentryNotifier
from .slack import SlackNotifier

manager = NotifierManager()
manager.add('sentry', SentryNotifier)
manager.add('slack', SlackNotifier)

get = manager.get
