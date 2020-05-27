__all__ = ["WebhookNotifier"]

from freight import http
from freight.models import App, Task, User

from .base import Notifier, generate_event_title


def stringify_date(date):
    return date.isoformat() + "Z" if date else None


class WebhookNotifier(Notifier):
    def get_options(self):
        return {"url": {"required": True}, "headers": {"required": False}}

    def send_deploy(self, deploy, task, config, event):
        url = config["url"]

        app = App.query.get(deploy.app_id)
        task = Task.query.get(deploy.task_id)
        user = User.query.get(task.user_id)
        title = generate_event_title(app, deploy, task, user, event)

        payload = {
            "app_name": app.name,
            "date_created": stringify_date(task.date_created),
            "date_started": stringify_date(task.date_started),
            "date_finished": stringify_date(task.date_finished),
            "deploy_number": deploy.number,
            "duration": task.duration,
            "environment": deploy.environment,
            "link": http.absolute_uri(
                f"/deploys/{app.name}/{deploy.environment}/{deploy.number}/"
            ),
            "params": dict(task.params or {}),
            "previous_sha": app.get_previous_sha(
                deploy.environment, current_sha=task.sha
            ),
            "ref": task.ref,
            "sha": task.sha,
            "status": str(event),
            "title": title,
            "user": user.name,
            "user_id": user.id,
        }

        http.post(url, headers=config.get("headers", {}), json=payload)
