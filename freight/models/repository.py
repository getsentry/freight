from __future__ import absolute_import

import os.path

from datetime import datetime
from flask import current_app
from sqlalchemy import Column, DateTime, Integer, String

from freight.config import db
from freight.db.types.json import JSONEncodedDict


class Repository(db.Model):
    __tablename__ = 'repository'

    id = Column(Integer, primary_key=True)
    url = Column(String(200), nullable=False, unique=True)
    vcs = Column(String(64), nullable=False)
    data = Column(JSONEncodedDict)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)

    def get_path(self):
        return os.path.join(
            current_app.config['WORKSPACE_ROOT'], 'freight-repo-{}'.format(self.id)
        )
