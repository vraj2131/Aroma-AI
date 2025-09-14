from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum as PyEnum

from app.models.status_base import StatusEnum


class Delivery(Base):
    __tablename__ = "delivery"
 
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    user_id = Column(Integer, ForeignKey("users.id"))  # Zomato, Swiggy, In-house
    address_id = Column(Integer, ForeignKey("addresses.id"))
    delivery_status = Column(String(100))
    expected_time = Column(DateTime, nullable=True)
    actual_time = Column(DateTime, nullable=True)
 
    # order = relationship("Order", back_populates="delivery")


