from sqlalchemy.orm import Session
from db.db_models import Profile
from datetime import datetime

class ProfileRepository:
    """
    Repository for handling user profiles.
    """

    def __init__(self, session: Session):
        self.session = session

    def get_by_telegram_id(self, telegram_id: str):
        return self.session.query(Profile).filter_by(telegram_id=telegram_id).first()

    def save(self, telegram_id: str, profile_data: dict):
        """
        Create or update a user profile based on Telegram ID.
        """
        profile = self.get_by_telegram_id(telegram_id)
        now = datetime.utcnow()

        if profile:
            for key, value in profile_data.items():
                setattr(profile, key, value)
            profile.updated_at = now
            return profile
        else:
            profile = Profile(
                telegram_id=telegram_id,
                created_at=now,
                updated_at=now,
                **profile_data
            )
            self.session.add(profile)
            return profile