from __future__ import absolute_import, unicode_literals

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String

from freight.config import db


class User(db.Model):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
