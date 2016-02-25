from __future__ import absolute_import

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.schema import Index

from freight.config import db
from freight.db.types.json import JSONEncodedDict


class TaskStatus(object):
    unknown = 0
    pending = 1
    in_progress = 2
    finished = 3
    failed = 4
    cancelled = 5

    @classmethod
    def get_label(cls, status):
        return STATUS_LABELS[status]

    @classmethod
    def label_to_id(cls, label):
        return STATUS_LABELS_REV[label]


STATUS_LABELS = {
    TaskStatus.unknown: 'unknown',
    TaskStatus.pending: 'pending',
    TaskStatus.in_progress: 'in_progress',
    TaskStatus.finished: 'finished',
    TaskStatus.failed: 'failed',
    TaskStatus.cancelled: 'cancelled',
}
STATUS_LABELS_REV = {
    v: k for k, v in STATUS_LABELS.items()
}


class Task(db.Model):
    __tablename__ = 'task'
    __table_args__ = (
        Index('idx_task_app_id', 'app_id'),
        Index('idx_task_user_id', 'user_id'),
    )

    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey('app.id', ondelete="CASCADE"),
                    nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete="CASCADE"),
                     nullable=False)
    ref = Column(String(128), nullable=False)
    sha = Column(String(40))
    provider = Column(String(64), nullable=False)
    status = Column(Integer, nullable=False)
    params = Column(JSONEncodedDict, nullable=True)
    data = Column(JSONEncodedDict)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
    # represents the start of the task (or the last time it was attempted)
    date_started = Column(DateTime)
    date_finished = Column(DateTime)

    @property
    def was_forced(self):
        return self.data.get('force', False)

    @property
    def checks(self):
        return self.data.get('checks', [])

    @property
    def notifiers(self):
        return self.data.get('notifiers', [])

    @property
    def provider_config(self):
        return self.data.get('provider_config', {})

    @property
    def status_label(self):
        return STATUS_LABELS.get(self.status, 'unknown')

    @property
    def duration(self):
        if not (self.date_finished and self.date_started):
            return
        return float('%.2f' % (self.date_finished - self.date_started).total_seconds())
