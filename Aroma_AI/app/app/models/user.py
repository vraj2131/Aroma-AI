# app/models/user.py
from datetime import datetime
from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects import postgresql

from app.db.base_class import Base
from app.models.status_base import UserRole, StatusEnum


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    access_token = Column(String, index=True)
    username = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    verified = Column(Boolean, default=False)
    status = Column(String, index=True)

    # waiting_list = relationship("waiting_list", backref="user")


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    access_token = Column(String, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    full_name = Column(String(150), nullable=True)
    phone = Column(String(20), unique=True, nullable=False)
    email = Column(String(150), unique=True)
    loyalty_points = Column(Integer, default=0)
    status = Column(String, index=True) #
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # addresses = relationship("Address", back_populates="customer", cascade="all, delete-orphan")

class UserOTP(Base):
    __tablename__ = 'user_otp'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, index=True)
    otp = Column(String, nullable=False)
    valid_until = Column(DateTime, nullable=False)
