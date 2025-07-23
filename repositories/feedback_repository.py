from sqlalchemy.orm import Session
from db.db_models import Feedback
from datetime import datetime

class FeedbackRepository:
    """
    Repository for handling feedback messages from users.
    """

    def __init__(self, session: Session):
        self.session = session

    def save(self, telegram_id: str, message: str):
        """
        Save a new feedback message from a user.
        """
        feedback = Feedback(
            telegram_id=telegram_id,
            message=message,
            submitted_at=datetime.utcnow()
        )
        self.session.add(feedback)
        return feedback