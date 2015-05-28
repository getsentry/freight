from __future__ import absolute_import

from datetime import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Text, Integer
from sqlalchemy.schema import Index, UniqueConstraint

from freight.config import db


LOG_CHUNK_SIZE = 4096


class LogChunk(db.Model):
    __tablename__ = 'logchunk'
    __table_args__ = (
        Index('idx_logchunk_task_id', 'task_id'),
        UniqueConstraint('task_id', 'offset', name='unq_logchunk_source_offset'),
    )

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey('task.id', ondelete="CASCADE"), nullable=False)
    # offset is sum(c.size for c in chunks_before_this)
    offset = Column(Integer, nullable=False)
    # size is len(text)
    size = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    date_created = Column(DateTime, default=datetime.utcnow, nullable=False)
