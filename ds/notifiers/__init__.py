from __future__ import absolute_import, unicode_literals

from .base import Notifier, NotifierEvent  # NOQA
from .manager import NotifierManager
from .slack import SlackNotifier

manager = NotifierManager()
manager.add('slack', SlackNotifier)

get = manager.get
