import uuid
from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base

class Outbox(Base):
    __tablename__ = "outbox"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    event_type = Column(String, nullable=False)
    payload = Column(JSON, nullable=False)

    status = Column(String, default="pending")

    created_at = Column(DateTime, server_default=func.now())