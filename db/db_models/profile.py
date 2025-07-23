from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from datetime import datetime
from db.base import Base

class Profile(Base):
    __tablename__ = 'profiles'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True)
    is_pregnant = Column(Boolean)
    has_children = Column(Boolean)
    children_count = Column(Integer)
    children_ages = Column(Text)
    country = Column(String)
    is_breastfeeding = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)