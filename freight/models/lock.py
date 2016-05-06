from __future__ import absolute_import

from datetime import datetime

from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.schema import Index, UniqueConstraint

from freight.config import db


class Lock(db.Model):
    __tablename__ = 'lock'
    __table_args__ = (
        Index('idx_lock_app_id', 'app_id'),
        Index('idx_lock_user_id', 'user_id'),
        UniqueConstraint('user_id', 'app_id', 'environment', 'date_locked', name='unq_lock_number'),
    )

    id = Column(Integer, primary_key=True)
    app_id = Column(Integer, ForeignKey('app.id', ondelete='CASCADE'),
                    nullable=False)
    user_id = Column(Integer, ForeignKey('user.id', ondelete='CASCADE'),
                    nullable=False)
    environment = Column(String(64), nullable=False, default='production')
    message = Column(String(140), nullable=False)
    date_locked = Column(DateTime, default=datetime.utcnow, nullable=False)
    date_unlocked = Column(DateTime)

    @property
    def is_active(self):
        return not self.date_unlocked

    @property
    def duration(self):
        if not self.date_unlocked:
            return
        return float('%.2f' % (self.date_locked - self.date_unlocked).total_seconds())

    @property
    def creator(self):
        from freight.models import User
        return User.query.filter(User.id == self.user_id).first()

    @property
    def app(self):
        from freight.models import App
        return App.query.filter(App.id == self.app_id).first()
