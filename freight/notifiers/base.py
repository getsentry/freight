from freight.models import Deploy, TaskStatus
from freight import http

__all__ = ["Notifier", "NotifierEvent"]


class NotifierEvent(object):
    TASK_STARTED = 0
    TASK_FINISHED = 1
    TASK_QUEUED = 2


class Notifier(object):
    DEFAULT_EVENTS = [
        NotifierEvent.TASK_QUEUED,
        NotifierEvent.TASK_STARTED,
        NotifierEvent.TASK_FINISHED,
    ]

    def get_default_options(self):
        return {
            # TODO(dcramer): we want to support events, but we need validators
            # before that can happen to avoid magical constants
            # 'events': {},
        }

    def get_options(self):
        return {}

    def send(self, task, config, event):
        # TODO(mattrobenolt): Split this out into send_deploy, send_x
        # since we want different notifications for different tasks,
        # and remove this shim. For now, we there are only deploys
        deploy = Deploy.query.filter(Deploy.task_id == task.id).first()
        return self.send_deploy(deploy, task, config, event)

    def send_deploy(self, deploy, task, config, event):
        raise NotImplementedError

    def should_send(self, task, config, event):
        deploy = Deploy.query.filter(Deploy.task_id == task.id).first()
        return self.should_send_deploy(deploy, task, config, event)

    def should_send_deploy(self, deploy, task, config, event):
        return event in config.get("events", self.DEFAULT_EVENTS)


def generate_event_title(app, deploy, task, user, event):
    number = deploy.number
    app_name = app.name
    params = dict(task.params or {})
    env = deploy.environment
    ref = task.ref
    sha = task.sha[:7] if task.sha else task.ref
    status_label = task.status_label
    duration = task.duration
    user = user.name.split("@", 1)[
        0
    ]  # Usernames can either be 'user' or 'user@example.com'
    link = http.absolute_uri(
        f"/deploys/{app.name}/{deploy.environment}/{deploy.number}"
    )

    # TODO(dcramer): show the ref when it differs from the sha
    if event == NotifierEvent.TASK_QUEUED:
        return f"[{app_name}/{env}] {user} queued deploy <{link}|#{number}> ({sha})"
    if event == NotifierEvent.TASK_STARTED:
        return "[{app_name}/{env}] {user} started deploy <{link}|#{number}> ({sha})"
    if task.status == TaskStatus.failed:
        return "[{app_name}/{env}] Failed to finish {user}'s deploy <{link}|#{number}> ({sha}) after {duration}s"
    if task.status == TaskStatus.cancelled:
        return "[{app_name}/{env}] {user}'s deploy <{link}|#{number}> ({sha}) was cancelled after {duration}s"
    if task.status == TaskStatus.finished:
        return "[{app_name}/{env}] Successfully finished {user}'s deploy <{link}|#{number}> ({sha}) after {duration}s"
    raise NotImplementedError(task.status)
