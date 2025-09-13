from sqlalchemy import (
    Column, Integer, String, DateTime, ForeignKey, Enum, Text, Float, Boolean
)
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base
import enum as PyEnum

from app.models.status_base import StatusEnum

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))  # column name lowercase
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=True)
    order_type = Column(String(100))
    status = Column(String, index=True)
    payment_status = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    feedbacks = relationship("Feedback", back_populates="order", cascade="all, delete-orphan")
    items = relationship("OrderItem", backref="order", cascade="all, delete-orphan")
    # customer = relationship("User", backref="order")
    # table = relationship("Table", backref="order")
    # items = relationship("OrderItem", backref="order", cascade="all, delete-orphan")
    # feedback = relationship("Feedback", backref="order", uselist=False)
    # delivery = relationship("Delivery", backref="order", uselist=False)
    # notifications = relationship("Notification", backref="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"))
    item_type = Column(String(50), index=True)
    item_name = Column(String(100))
    customization = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    price = Column(Float)

    # order = relationship("Order", backref="items")  # corrected: 'order' matches Order.items


class MenuItem(Base):
    __tablename__ = "menu_items"

    id = Column(Integer, primary_key=True, index=True)
    item_type = Column(String(50), index=True)  # main_course, starter, dessert, beverage
    item_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    is_available = Column(Boolean, default=True)