from __future__ import absolute_import, unicode_literals

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func, select

from freight.config import db


class TaskSequence(db.Model):
    __tablename__ = 'tasksequence'

    app_id = Column(Integer, nullable=False, primary_key=True)
    environment = Column(String(64), nullable=False, primary_key=True)
    value = Column(Integer, default=0, server_default='0', nullable=False,
                   primary_key=True)

    @classmethod
    def get_clause(self, app_id, environment):
        return select([func.next_task_number(app_id, environment)])
