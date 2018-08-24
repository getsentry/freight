from __future__ import absolute_import

__all__ = ['CraftProvider']

from .base import Provider
from freight.models import Deploy


class CraftProvider(Provider):
    def get_options(self):
        return {
            'env': {'required': False, 'type': dict},
        }

    def execute(self, workspace, task):
        deploy = Deploy.query.filter(Deploy.task_id == task.id).first()
        return self.run_release(workspace, deploy, task)

    def run_release(self, workspace, deploy, task):
        # TODO this should be wrapped into a serializer/validator
        no_merge = bool(task.params.get("noMerge"))
        no_status_check = bool(task.params.get("noStatusCheck"))

        executable = "craft"

        args = ["publish"]
        args.append(str(task.params.get("newVersion")))
        args.append("--no-merge={}".format(str(no_merge).lower()))
        args.append("--no-status-check={}".format(str(no_status_check).lower()))

        command = "{executable} {args}".format(executable=executable, args=" ".join(args))

        return workspace.run(command, env=task.provider_config.get("env"))
