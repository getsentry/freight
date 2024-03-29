from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.schema import Index

from freight.config import db
from freight.db.types.json import JSONEncodedDict

DEFAULT_REF = "master"


class App(db.Model):
    """
    Example App configuration:

    {
        "environments": {
            "production": {
                "default_ref": "master"
            }
        },
        # change_labels provides a way for the app to specify what remote PR
        # labels should be used to filter / mark which changes are displayed in
        # the commit list in the 'Create Deploy' UI.
        #
        # This is especially useful for apps where changes in the repo do not
        # always map directly to a deployed application, and we want to only
        # indicate that a subset of changes are going to be deployed.
        "change_labels": ["Scope: Backend"]
    }
    """

    __tablename__ = "app"
    __table_args__ = (Index("idx_app_repository_id", "repository_id"),)

    id = Column(Integer, primary_key=True)
    repository_id = Column(
        Integer, ForeignKey("repository.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String(200), nullable=False, unique=True)
    provider = Column(String(64))
    data = Column(JSONEncodedDict)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    locked_reason = Column(Text)

    @property
    def environments(self):
        return self.data.get("environments", {})

    @property
    def change_labels(self):
        return self.data.get("change_labels", [])

    @property
    def deploy_config(self):
        from freight.models import TaskConfig, TaskConfigType

        return TaskConfig.query.filter(
            TaskConfig.app_id == self.id, TaskConfig.type == TaskConfigType.deploy
        ).first()

    def get_default_ref(self, env):
        data = self.environments.get(env)
        if not data:
            return DEFAULT_REF
        return data.get("default_ref", DEFAULT_REF)

    def get_current_sha(self, env):
        from freight.models import Task, Deploy, TaskStatus

        return (
            db.session.query(Task.sha)
            .filter(
                Deploy.task_id == Task.id,
                Task.app_id == self.id,
                Deploy.environment == env,
                Task.status == TaskStatus.finished,
            )
            .order_by(Deploy.number.desc())
            .limit(1)
            .scalar()
        )

    def get_previous_sha(self, env, current_sha=None):
        from freight.models import Task, Deploy, TaskStatus

        if current_sha is None:
            current_sha = self.get_current_sha(env)

        if current_sha is None:
            return None

        return (
            db.session.query(Task.sha)
            .filter(
                Deploy.task_id == Task.id,
                Task.app_id == self.id,
                Deploy.environment == env,
                Task.status == TaskStatus.finished,
                Task.sha != current_sha,
            )
            .order_by(Deploy.number.desc())
            .limit(1)
            .scalar()
        )
