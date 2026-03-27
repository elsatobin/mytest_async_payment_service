from sqlalchemy import Column, DateTime, Integer, JSON, String
import uuid
from sqlalchemy.sql import func

from app.db.base import Base


class Outbox(Base):
    __tablename__ = "outbox"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="pending")
    retry_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, server_default=func.now())