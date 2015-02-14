from __future__ import absolute_import, unicode_literals

__all__ = ['ShellProvider']

from .base import Provider


class ShellProvider(Provider):
    def get_options(self):
        return {
            'command': {'required': True},
        }

    def get_command(self, task):
        ssh_key = self.get_ssh_key()

        return task.provider_config['command'].format(
            environment=task.environment,
            sha=task.sha,
            ref=task.ref,
            task=task.name,
            ssh_key=ssh_key.name if ssh_key else '~/.ssh/id_rsa',
        )

    def execute(self, workspace, task):
        command = self.get_command(task)
        return workspace.run(command)
