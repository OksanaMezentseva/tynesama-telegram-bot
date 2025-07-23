from sqlalchemy.orm import Session
from db.db_models import User

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_telegram_id(self, telegram_id: str) -> User:
        return self.session.query(User).filter_by(telegram_id=telegram_id).first()

    def create(self, telegram_id: str) -> User:
        user = User(telegram_id=telegram_id)
        self.session.add(user)
        return user

    def update_state(self, telegram_id: str, state: str):
        user = self.get_by_telegram_id(telegram_id)
        if user:
            user.user_state = state
        return user

    def set_subscription(self, telegram_id: str, is_subscribed: bool):
        user = self.get_by_telegram_id(telegram_id)
        if user:
            user.is_subscribed = is_subscribed

    def get_all_subscribed_users(self):
        return self.session.query(User).filter_by(is_subscribed=True).all()