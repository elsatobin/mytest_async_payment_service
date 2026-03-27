from sqlalchemy import Column, String, Boolean, JSON, Integer
import uuid

from app.db.base import Base


class Outbox(Base):
    __tablename__ = "outbox"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String)
    payload = Column(JSON)

    processed = Column(Boolean, default=False)

    retry_count = Column(Integer, default=0)  # 🔥 추가