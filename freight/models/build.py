from __future__ import absolute_import

from sqlalchemy import Column, ForeignKey, Integer
from sqlalchemy.schema import Index, UniqueConstraint

from freight.config import db


class Build(db.Model):
    __tablename__ = 'build'
    __table_args__ = (
        Index('idx_build_task_id', 'task_id'),
        Index('idx_build_app_id', 'app_id'),
        UniqueConstraint('task_id', 'app_id', 'number', name='unq_build_number'),
    )

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'),
                    nullable=False)
    app_id = Column(Integer, ForeignKey('app.id', ondelete='CASCADE'),
                    nullable=False)
    number = Column(Integer, nullable=False)
