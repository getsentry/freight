from __future__ import absolute_import, unicode_literals

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.schema import Index

from freight.config import db
from freight.db.types.json import JSONEncodedDict


class App(db.Model):
    __tablename__ = 'app'
    __table_args__ = (
        Index('idx_app_repository_id', 'repository_id'),
    )

    id = Column(Integer, primary_key=True)
    repository_id = Column(Integer,
                           ForeignKey('repository.id', ondelete="CASCADE"),
                           nullable=False)
    name = Column(String(200), nullable=False, unique=True)
    provider = Column(String(64))
    data = Column(JSONEncodedDict)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)

    @property
    def checks(self):
        return self.data.get('checks', [])

    @property
    def notifiers(self):
        return self.data.get('notifiers', [])

    @property
    def provider_config(self):
        return self.data.get('provider_config', {})
