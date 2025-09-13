from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum as PyEnum

from app.models.status_base import StatusEnum


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    address_line = Column(Text, nullable=False)
    city = Column(String(100), nullable=True)
    state = Column(String(100), nullable=True)
    postal_code = Column(String(20), nullable=True)
    address_type = Column(String(50), default="home") # e.g. home, office, billing, shipping
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # customer = relationship("Customer", back_populates="addresses")

