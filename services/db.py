from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL
import json

# Initialize the database engine
engine = create_engine(DATABASE_URL)

# Create a session to interact with the database
Session = sessionmaker(bind=engine)
session = Session()

# Base class for declarative models
Base = declarative_base()

# Define the User model/table
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)  # Auto-incremented primary key
    telegram_id = Column(String, unique=True, nullable=False)  # Unique Telegram user ID
    user_state = Column(Text)  # Serialized JSON with state/context for the user
    is_subscribed = Column(Boolean, default=True)  # Subscription status (True = subscribed)
    subscribed_at = Column(DateTime, default=datetime.utcnow)  # When the user subscribed
    started_at = Column(DateTime, default=datetime.utcnow)  # When the user first interacted with the bot

# Create all tables (if not already created)
Base.metadata.create_all(engine)

# Add a new user to the database (if they don't already exist)
def add_user(telegram_id):
    existing_user = session.query(User).filter_by(telegram_id=telegram_id).first()
    if not existing_user:
        user = User(
            telegram_id=telegram_id,
            user_state=json.dumps({}),  # Default empty user state
            is_subscribed=True,
            subscribed_at=datetime.utcnow(),
            started_at=datetime.utcnow()
        )
        session.add(user)
        session.commit()
        
def get_user(telegram_id):
    return session.query(User).filter_by(telegram_id=telegram_id).first()
