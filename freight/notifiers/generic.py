__all__ = ["GenericNotifier"]

from freight import http
from freight.models import App, Task, TaskStatus, User

from .base import Notifier, NotifierEvent, generate_event_title


class GenericNotifier(Notifier):
    def get_options(self):
        return {"webhook_url": {"required": True}}

    def should_send_deploy(self, deploy, task, config, event):
        if event == NotifierEvent.TASK_STARTED:
            return True

        if event == NotifierEvent.TASK_FINISHED and task.status == TaskStatus.finished:
            return True

        return False

    def send_deploy(self, deploy, task, config, event):
        webhook_url = config["webhook_url"]

        app = App.query.get(deploy.app_id)
        task = Task.query.get(deploy.task_id)
        user = User.query.get(task.user_id)
        title = generate_event_title(app, deploy, task, user, event)

        payload = {
            "app_name": app.name,
            "environment": deploy.environment,
            "deploy_number": deploy.number,
            "title": title,
            "status": str(event),
            "ref": task.ref,
            "sha": task.sha,
            "previous_sha": app.get_previous_sha(deploy.environment, current_sha=task.sha),
            "date_created": task.date_created,
            "date_started": task.date_started,
            "date_finished": task.date_finished,
            "user": user.name,
            "user_id": user.id,
        }

        http.post(webhook_url, json=payload)
