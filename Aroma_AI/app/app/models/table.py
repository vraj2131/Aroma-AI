from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum as PyEnum

from app.models.status_base import StatusEnum

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    number = Column(Integer, unique=True)
    status = Column(String(50), default="available")  # available / occupied / cleaning
    seats = Column(Integer)

    orders = relationship("Order", back_populates="table")


