from __future__ import absolute_import

__all__ = ['BuildStatusCheck']

import logging

from freight.exceptions import CheckFailed, CheckPending
from freight.models import Build, Task

from .base import Check

CHECK = 'Build for {} {} {}.'
logger = logging.getLogger(__name__)


class BuildStatusCheck(Check):
    def check(self, app, sha, config):
        build = Build.query.filter(
            Build.app_id == app.id,
            Task.sha == sha,
        ).first()

        label = '{}:{}'.format(app.name, sha)

        if not build:
            raise CheckFailed(CHECK.format(label, 'was', 'not found'))

        status = Task.query.get(build.task_id).status_label

        if status in ['pending', 'in_progress']:
            raise CheckPending(CHECK.format(label, 'is', status))
        elif status != 'success':
            raise CheckFailed(CHECK.format(label, 'was', status))
        logger.debug(CHECK.format(label, 'was', status))
