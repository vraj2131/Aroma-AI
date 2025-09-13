from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum as PyEnum

from app.models.status_base import StatusEnum


class Reward(Base):
    __tablename__ = "rewards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String(50))  # discount / subscription / coupon
    points = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
