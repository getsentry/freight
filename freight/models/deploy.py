from __future__ import absolute_import

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.schema import Index, UniqueConstraint

from freight.config import db


class Deploy(db.Model):
    __tablename__ = 'deploy'
    __table_args__ = (
        Index('idx_deploy_task_id', 'task_id'),
        Index('idx_deploy_app_id', 'app_id'),
        UniqueConstraint('task_id', 'app_id', 'environment', 'number', name='unq_deploy_number'),
    )

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id', ondelete='CASCADE'),
                    nullable=False)
    app_id = Column(Integer, ForeignKey('app.id', ondelete='CASCADE'),
                    nullable=False)
    environment = Column(String(64), nullable=False, default='production')
    number = Column(Integer, nullable=False)
