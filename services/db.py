import logging
import json
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import DATABASE_URL

Base = declarative_base()
_engine = None
_Session = None

# Lazily initialize DB engine/session
def get_session():
    global _engine, _Session
    if _engine is None:
        _engine = create_engine(
            DATABASE_URL,
            pool_pre_ping=True,
            pool_recycle=1800
        )
        _Session = sessionmaker(bind=_engine)
        Base.metadata.create_all(_engine)
        logging.info("🗃️ Database engine initialized")
    return _Session()

# User model
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, unique=True, nullable=False)
    user_state = Column(Text)
    is_subscribed = Column(Boolean, default=True)
    subscribed_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, default=datetime.utcnow)

# Feedback model
class Feedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    submitted_at = Column(DateTime, default=datetime.utcnow)

# Database functions
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

def get_user_state(telegram_id):
    user = get_user(telegram_id)
    if user and user.user_state:
        try:
            return json.loads(user.user_state)
        except json.JSONDecodeError:
            logging.warning(f"⚠️ Corrupted user_state for {telegram_id}")
            return {}
    return {}

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

def get_all_subscribed_users():
    session = get_session()
    try:
        return session.query(User).filter_by(is_subscribed=True).all()
    except Exception as e:
        logging.warning(f"❌ DB error in get_all_subscribed_users: {e}")
        return []
    finally:
        session.close()

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