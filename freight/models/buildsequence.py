from __future__ import absolute_import

from sqlalchemy import Column, Integer
from sqlalchemy.sql import func, select

from freight.config import db


class BuildSequence(db.Model):
    __tablename__ = 'buildsequence'

    app_id = Column(Integer, nullable=False, primary_key=True)
    value = Column(Integer, default=0, server_default='0', nullable=False,
                   primary_key=True)

    @classmethod
    def get_clause(self, app_id):
        return select([func.next_build_number(app_id)])
