from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from db.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    user_state = Column(Text)
    is_subscribed = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, default=datetime.utcnow)