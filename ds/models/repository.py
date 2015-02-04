from __future__ import absolute_import

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String

from ds.config import db
from ds.db.types.json import JSONEncodedDict


class Repository(db.Model):
    __tablename__ = 'repository'

    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False, unique=True)
    vcs = Column(String(64), nullable=False)
    data = Column(JSONEncodedDict)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
