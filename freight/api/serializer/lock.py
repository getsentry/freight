from __future__ import absolute_import

from freight.models import Lock

from freight.api.serializer import serialize

from .base import Serializer
from .manager import add


@add(Lock)
class LockSerializer(Serializer):
    def serialize(self, item, attrs):
        app = item.app
        creator = item.creator
        return {
            'id': str(item.id),
            'name': '{} ({})'.format(app.name, creator.name),
            'app': serialize(item.app),
            'creator': serialize(item.creator),
            'environment': item.environment,
            'message': item.message,
            'dateLocked': self.format_datetime(item.date_locked),
            'dateUnlocked': self.format_datetime(item.date_unlocked),
        }
