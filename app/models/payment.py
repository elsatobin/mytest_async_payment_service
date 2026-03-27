import uuid
from sqlalchemy import DateTime, Numeric, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import Column

from app.db.base import Base

class Payment(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    amount = Column(Numeric, nullable=False)
    currency = Column(String(3), nullable=False)
    description = Column(String)
    meta = Column(JSON)

    status = Column(String(20), nullable=False, default="pending")

    idempotency_key = Column(String, unique=True, nullable=False)
    webhook_url = Column(String, nullable=False)

    created_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime, nullable=True)