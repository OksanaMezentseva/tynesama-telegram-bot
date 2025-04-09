from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from config import DATABASE_URL
import json

# Initialize the database engine and session
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

# Base class for declarative models
Base = declarative_base()

# User table definition
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    user_state = Column(Text)
    is_subscribed = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, default=datetime.utcnow)

# Create the table
Base.metadata.create_all(engine)

# Add a new user
def add_user(telegram_id):
    telegram_id = str(telegram_id)
    try:
        existing_user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if not existing_user:
            user = User(
                telegram_id=telegram_id,
                user_state=json.dumps({}),
                is_subscribed=True,
                subscribed_at=datetime.utcnow(),
                started_at=datetime.utcnow()
            )
            session.add(user)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ DB error in add_user: {e}")

# Get user object
def get_user(telegram_id):
    telegram_id = str(telegram_id)
    try:
        return session.query(User).filter_by(telegram_id=telegram_id).first()
    except Exception as e:
        print(f"❌ DB error in get_user: {e}")
        return None

# Get user state as dict
def get_user_state(telegram_id):
    user = get_user(telegram_id)
    if user and user.user_state:
        try:
            return json.loads(user.user_state)
        except json.JSONDecodeError:
            return {}
    return {}

# Update user state
def update_user_state(telegram_id, data: dict):
    telegram_id = str(telegram_id)
    try:
        user = get_user(telegram_id)
        if user:
            user.user_state = json.dumps(data)
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ DB error in update_user_state: {e}")

# Set subscription status
def set_subscription_status(telegram_id, is_subscribed: bool):
    telegram_id = str(telegram_id)
    try:
        user = get_user(telegram_id)
        if user:
            user.is_subscribed = is_subscribed
            if is_subscribed:
                user.subscribed_at = datetime.utcnow()
            session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ DB error in set_subscription_status: {e}")

# Get all subscribed users
def get_all_subscribed_users():
    try:
        return session.query(User).filter_by(is_subscribed=True).all()
    except Exception as e:
        print(f"❌ DB error in get_all_subscribed_users: {e}")
        return []
    
# Feedback table definition
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

# Create feedback table if it doesn't exist
Base.metadata.create_all(engine)

# Save feedback to the database
def save_feedback(telegram_id, message: str):
    telegram_id = str(telegram_id)
    try:
        feedback = Feedback(
            telegram_id=telegram_id,
            message=message,
            submitted_at=datetime.utcnow()
        )
        session.add(feedback)
        session.commit()
        print("✅ Feedback saved to database.")
    except Exception as e:
        session.rollback()
        print(f"❌ DB error in save_feedback: {e}")
