from __future__ import absolute_import

from freight.models import App, Repository, TaskConfig

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

        if item.repository_id:
            repo = Repository.query.filter(Repository.id == item.repository_id).first().url
        else:
            repo = None

        # Let's assume that we have only one TaskConfig per App for now
        task_config = TaskConfig.query.filter(
            TaskConfig.app_id == item.id,
        ).first()

        return {
            'id': str(item.id),
            'name': item.name,
            'environments': env_map,
            'type': task_config.type,
            'repository': repo,
        }
