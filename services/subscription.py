from db.session import SessionLocal
from repositories.user_repository import UserRepository


def add_subscriber(telegram_id: str):
    """
    Mark a user as subscribed (if not already) and update their subscription timestamp.
    """
    session = SessionLocal()
    try:
        repo = UserRepository(session)
        user = repo.get_by_telegram_id(telegram_id)
        if user and not user.is_subscribed:
            repo.set_subscription(telegram_id, True)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def remove_subscriber(telegram_id: str):
    """
    Mark a user as unsubscribed (if currently subscribed).
    """
    session = SessionLocal()
    try:
        repo = UserRepository(session)
        user = repo.get_by_telegram_id(telegram_id)
        if user and user.is_subscribed:
            repo.set_subscription(telegram_id, False)
            session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def is_subscribed(telegram_id: str) -> bool:
    """
    Check whether a user is currently subscribed.
    """
    session = SessionLocal()
    try:
        repo = UserRepository(session)
        user = repo.get_by_telegram_id(telegram_id)
        return user.is_subscribed if user else False
    except Exception:
        return False
    finally:
        session.close()