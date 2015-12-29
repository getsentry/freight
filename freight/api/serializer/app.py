from __future__ import absolute_import

from freight.models import App

from .base import Serializer
from .manager import add


@add(App)
class AppSerializer(Serializer):
    def serialize(self, item, attrs):
        env_map = {}
        for env, env_data in item.environments.iteritems():
            env_map[env] = {
                'defaultRef': env_data.get('default_ref', 'master'),
            }

        if not env_map:
            env_map['production'] = {
                'defaultRef': 'master',
            }

        return {
            'id': str(item.id),
            'name': item.name,
            'environments': env_map,
        }
