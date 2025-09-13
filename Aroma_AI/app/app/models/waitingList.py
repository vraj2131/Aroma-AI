# app/models/user.py
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum, Date, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql
from app.db.base_class import Base

class WaitingList(Base):
    __tablename__ = "waiting_list"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    booking_date = Column(Date, default=func.current_date(), nullable=False)
    position = Column(Integer, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    user = relationship("User", backref="waiting_list")
