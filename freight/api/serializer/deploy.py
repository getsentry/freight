from datetime import datetime, timedelta
from sqlalchemy.sql import func

from freight import vcsremote
from freight.config import db
from freight.models import App, Task, Deploy, TaskStatus, User, Repository

from .base import Serializer
from .manager import add, serialize


@add(Deploy)
class DeploySerializer(Serializer):
    def get_attrs(self, item_list):
        apps = {
            a.id: a for a in App.query.filter(App.id.in_({i.app_id for i in item_list}))
        }

        repos = {
            r.id: r
            for r in Repository.query.filter(
                Repository.id.in_({a.repository_id for a in apps.values()})
            )
        }

        tasks = {
            t.id: t
            for t in Task.query.filter(Task.id.in_({i.task_id for i in item_list}))
        }

        estimatedDurations = dict(
            db.session.query(
                Task.app_id, func.avg(Task.date_finished - Task.date_started)
            )
            .filter(
                Task.date_finished > datetime.utcnow() - timedelta(days=7),
                Task.status == TaskStatus.finished,
            )
            .group_by(Task.app_id)
        )

        user_ids = {tasks[d.task_id].user_id for d in item_list}
        if user_ids:
            user_map = {u.id: u for u in User.query.filter(User.id.in_(user_ids))}
        else:
            user_map = {}

        attrs = {}
        for item in item_list:
            estimatedDuration = estimatedDurations.get(tasks[item.task_id].app_id)
            if estimatedDuration:
                estimatedDuration = estimatedDuration.total_seconds()

            attrs[item] = {
                "app": apps[item.app_id],
                "repo": repos[apps[item.app_id].repository_id],
                "task": tasks[item.task_id],
                "user": user_map.get(tasks[item.task_id].user_id),
                "estimatedDuration": estimatedDuration,
            }
        return attrs

    def serialize(self, item, attrs):
        app = attrs["app"]
        task = attrs["task"]
        repo = attrs["repo"]

        vcs_remote = vcsremote.get_by_repo(repo)

        return {
            "id": str(item.id),
            "name": f"{app.name}/{item.environment}#{item.number}",
            "app": {"id": str(app.id), "name": app.name},
            "remote": {"name": vcs_remote.hostname, "url": vcs_remote.repo_url},
            "user": serialize(attrs["user"]),
            "environment": item.environment,
            "sha": task.sha,
            "sha_url": vcs_remote.get_commit_url(task.sha),
            "ref": task.ref,
            "number": item.number,
            "status": task.status_label,
            "duration": task.duration,
            "estimatedDuration": task.duration or attrs["estimatedDuration"],
            "dateCreated": self.format_datetime(task.date_created),
            "dateStarted": self.format_datetime(task.date_started),
            "dateFinished": self.format_datetime(task.date_finished),
        }
