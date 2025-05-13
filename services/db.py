import logging
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from config import DATABASE_URL

# SQLAlchemy base class
Base = declarative_base()

# Engine and session factory (initialized once at startup)
_engine = None
_Session = None

# Initialize database and create tables
def init_db():
    global _engine, _Session
    _engine = create_engine(
        DATABASE_URL,
        pool_pre_ping=True,     # automatically checks if connections are alive
        pool_recycle=1800       # recycle connections every 30 minutes
    )
    session_factory = sessionmaker(bind=_engine)
    _Session = scoped_session(session_factory)
    Base.metadata.create_all(_engine)
    logging.info("🗃️ Database initialized")

# Get an active session (requires init_db() to be called first)
def get_session():
    global _engine, _Session
    if _engine is None or _Session is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")
    return _Session()

# User table model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    user_state = Column(Text)
    is_subscribed = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, default=datetime.utcnow)

# Feedback table model
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

# Profile table model
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

# Add a new user if not already in the database
def add_user(telegram_id):
    telegram_id = str(telegram_id)
    session = get_session()
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
            logging.info(f"👤 New user added: {telegram_id}")
    except Exception as e:
        session.rollback()
        logging.warning(f"❌ DB error in add_user: {e}")
    finally:
        session.close()

# Get user object by Telegram ID
def get_user(telegram_id):
    telegram_id = str(telegram_id)
    session = get_session()
    try:
        return session.query(User).filter_by(telegram_id=telegram_id).first()
    except Exception as e:
        logging.warning(f"❌ DB error in get_user: {e}")
        return None
    finally:
        session.close()

# Get user state as dictionary
def get_user_state(telegram_id):
    user = get_user(telegram_id)
    if user and user.user_state:
        try:
            return json.loads(user.user_state)
        except json.JSONDecodeError:
            logging.warning(f"⚠️ Corrupted user_state for {telegram_id}")
            return {}
    return {}

# Update the user's state
def update_user_state(telegram_id, data: dict):
    telegram_id = str(telegram_id)
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.user_state = json.dumps(data)
            session.commit()
    except Exception as e:
        session.rollback()
        logging.warning(f"❌ DB error in update_user_state: {e}")
    finally:
        session.close()

# Update subscription status (subscribe/unsubscribe)
def set_subscription_status(telegram_id, is_subscribed: bool):
    telegram_id = str(telegram_id)
    session = get_session()
    try:
        user = session.query(User).filter_by(telegram_id=telegram_id).first()
        if user:
            user.is_subscribed = is_subscribed
            if is_subscribed:
                user.subscribed_at = datetime.utcnow()
            session.commit()
            logging.info(f"🔔 Subscription updated: {telegram_id} -> {is_subscribed}")
    except Exception as e:
        session.rollback()
        logging.warning(f"❌ DB error in set_subscription_status: {e}")
    finally:
        session.close()

# Get all users who are currently subscribed
def get_all_subscribed_users():
    session = get_session()
    try:
        return session.query(User).filter_by(is_subscribed=True).all()
    except Exception as e:
        logging.warning(f"❌ DB error in get_all_subscribed_users: {e}")
        return []
    finally:
        session.close()

# Save feedback message from a user
def save_feedback(telegram_id, message: str):
    telegram_id = str(telegram_id)
    session = get_session()
    try:
        feedback = Feedback(
            telegram_id=telegram_id,
            message=message,
            submitted_at=datetime.utcnow()
        )
        session.add(feedback)
        session.commit()
        logging.info(f"💬 Feedback saved from user {telegram_id}")
    except Exception as e:
        session.rollback()
        logging.warning(f"❌ DB error in save_feedback: {e}")
    finally:
        session.close()

# Save or update a user's profile
def save_profile(telegram_id: str, profile_data: dict):
    """
    Insert or update profile information for a given user.
    If a profile already exists, update it. Otherwise, create a new one.
    """
    telegram_id = str(telegram_id)
    session = get_session()
    try:
        existing_profile = session.query(Profile).filter_by(telegram_id=telegram_id).first()

        if existing_profile:
            # Update existing profile
            existing_profile.is_pregnant = profile_data.get("is_pregnant")
            existing_profile.has_children = profile_data.get("has_children")
            existing_profile.children_count = profile_data.get("children_count")
            existing_profile.children_ages = profile_data.get("children_ages")
            existing_profile.country = profile_data.get("country")
            existing_profile.is_breastfeeding = profile_data.get("is_breastfeeding")
            existing_profile.updated_at = datetime.utcnow()
            logging.info(f"🔄 Updated profile for user {telegram_id}")
        else:
            # Insert new profile
            new_profile = Profile(
                telegram_id=telegram_id,
                is_pregnant=profile_data.get("is_pregnant"),
                has_children=profile_data.get("has_children"),
                children_count=profile_data.get("children_count"),
                children_ages=profile_data.get("children_ages"),
                country=profile_data.get("country"),
                is_breastfeeding=profile_data.get("is_breastfeeding"),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            session.add(new_profile)
            logging.info(f"🆕 Created new profile for user {telegram_id}")

        session.commit()
    except Exception as e:
        session.rollback()
        logging.warning(f"❌ DB error in save_profile: {e}")
    finally:
        session.close()
