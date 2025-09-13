from datetime import datetime

from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey, Date, DateTime
from app.models import User
from app.db.base_class import Base


class Document(Base):
    __tablename__ = 'document'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(User.id))
    uploaded_at = Column(DateTime, default=datetime.utcnow, index=True)