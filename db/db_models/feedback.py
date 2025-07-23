from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from db.base import Base

class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)