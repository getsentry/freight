__all__ = ["ShellProvider"]

from .base import Provider
from freight.models import App, Deploy


class ShellProvider(Provider):
    def get_options(self):
        return {"command": {"required": True}, "env": {"required": False, "type": dict}}

    def get_command(self, deploy, task, ssh_key):
        params = task.params or {}

        app = App.query.get(task.app_id)
        prev_sha = app.get_previous_sha(deploy.environment, current_sha=task.sha)

        return task.provider_config["command"].format(
            environment=deploy.environment,
            sha=task.sha,
            prev_sha=prev_sha or "",
            ref=task.ref,
            ssh_key=ssh_key,
            params=params,
        )

    def execute(self, workspace, task):
        deploy = Deploy.query.filter(Deploy.task_id == task.id).first()
        return self.execute_deploy(workspace, deploy, task)

    def execute_deploy(self, workspace, deploy, task):
        # keep ssh_key in scope to ensure it doesnt get wiped until run() exits
        ssh_key = self.get_ssh_key()

        command = self.get_command(
            deploy=deploy,
            task=task,
            ssh_key=ssh_key.name if ssh_key else "~/.ssh/id_rsa",
        )
        return workspace.run(command, env=task.provider_config.get("env"))
