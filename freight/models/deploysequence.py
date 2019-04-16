from sqlalchemy import Column, Integer, String
from sqlalchemy.sql import func, select

from freight.config import db


class DeploySequence(db.Model):
    __tablename__ = "deploysequence"

    app_id = Column(Integer, nullable=False, primary_key=True)
    environment = Column(String(64), nullable=False, primary_key=True)
    value = Column(
        Integer, default=0, server_default="0", nullable=False, primary_key=True
    )

    @classmethod
    def get_clause(self, app_id, environment):
        return select([func.next_deploy_number(app_id, environment)])
