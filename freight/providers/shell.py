from __future__ import absolute_import

__all__ = ['ShellProvider']

from .base import Provider


class ShellProvider(Provider):
    def get_options(self):
        return {
            'command': {'required': True},
            'env': {'required': False, 'type': dict},
        }

    def get_command(self, task, ssh_key):
        params = task.params or {}

        return task.provider_config['command'].format(
            environment=task.environment,
            sha=task.sha,
            ref=task.ref,
            ssh_key=ssh_key,
            **params
        )

    def execute(self, workspace, task):
        # keep ssh_key in scope to ensure it doesnt get wiped until run() exits
        ssh_key = self.get_ssh_key()

        command = self.get_command(
            task=task,
            ssh_key=ssh_key.name if ssh_key else '~/.ssh/id_rsa',
        )
        return workspace.run(command, env=task.provider_config.get('env'))
