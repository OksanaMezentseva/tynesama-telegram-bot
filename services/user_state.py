import json
import logging
from db.session import SessionLocal
from repositories.user_repository import UserRepository

class UserStateManager:
    def __init__(self, telegram_id: str):
        self.telegram_id = str(telegram_id)
        self._state = self._load_state()

    def _load_state(self) -> dict:
        """
        Load the user's saved state from the database and parse as JSON.
        """
        session = SessionLocal()
        try:
            repo = UserRepository(session)
            user = repo.get_by_telegram_id(self.telegram_id)
            if user and user.user_state:
                try:
                    return json.loads(user.user_state)
                except json.JSONDecodeError:
                    logging.warning(f"⚠️ Failed to decode state for user {self.telegram_id}")
        except Exception as e:
            logging.error(f"❌ Error loading state for {self.telegram_id}: {e}")
        finally:
            session.close()
        return {}

    def _save_state(self):
        """
        Save the current state dictionary back to the database.
        """
        session = SessionLocal()
        try:
            repo = UserRepository(session)
            repo.update_state(self.telegram_id, json.dumps(self._state))
            session.commit()
            logging.debug(f"💾 State saved for user {self.telegram_id}")
        except Exception as e:
            session.rollback()
            logging.warning(f"❌ DB error in _save_state: {e}")
        finally:
            session.close()

    def get_state(self) -> dict:
        return self._state

    def set_state(self, new_state: dict):
        self._state = new_state
        self._save_state()

    def get(self, key: str, default=None):
        return self._state.get(key, default)

    def set(self, key: str, value):
        self._state[key] = value
        self._save_state()

    def get_step(self) -> str:
        return self.get("step", "")

    def set_step(self, step: str):
        self.set("step", step)

    def add_gpt_interaction(self, question: str, reply: str):
        """
        Add the latest GPT interaction to the state history.
        """
        topic = self.get("topic", "general")

        history_by_topic = self._state.get("history", {})
        topic_history = history_by_topic.get(topic, [])

        topic_history.append({
            "question": question,
            "reply": reply
        })

        history_by_topic[topic] = topic_history
        self._state["history"] = history_by_topic
        self._state["last_gpt_reply"] = reply
        self._state["last_question"] = question
        self._state["gpt_reply_count"] = self._state.get("gpt_reply_count", 0) + 1

        self._save_state()
        logging.debug(f"🧠 GPT interaction added for user {self.telegram_id}, topic: {topic}")

    def get_gpt_history(self, topic: str = None):
        """
        Return the last GPT interactions for the current topic.
        """
        if topic is None:
            topic = self.get("topic", "general")
        history = self._state.get("history", {})
        return history.get(topic, [])

    # ----------------------
    # Profile-specific helpers
    # ----------------------

    def get_profile_data(self) -> dict:
        """Return user's profile data dictionary."""
        return self._state.get("profile_data", {})

    def set_profile_data(self, data: dict):
        """Set and save user's profile data."""
        self._state["profile_data"] = data
        self._save_state()

    def increment_profile_progress(self):
        """Increment the current profile step progress counter."""
        current = self.get("profile_progress", 0)
        self.set("profile_progress", current + 1)