import json
import os
from datetime import datetime

SUBSCRIBERS_FILE = "subscribers.json"


def load_subscribers():
    """Load subscribers from JSON file."""
    if not os.path.exists(SUBSCRIBERS_FILE):
        return {}
    with open(SUBSCRIBERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_subscribers(subscribers):
    """Save subscribers to JSON file."""
    with open(SUBSCRIBERS_FILE, "w", encoding="utf-8") as f:
        json.dump(subscribers, f, ensure_ascii=False, indent=2)


def add_subscriber(chat_id):
    """Add a subscriber with timestamp if not already subscribed."""
    chat_id = str(chat_id)
    subscribers = load_subscribers()
    if chat_id not in subscribers:
        subscribers[chat_id] = {
            "subscribed_at": datetime.utcnow().isoformat()
        }
        save_subscribers(subscribers)


def remove_subscriber(chat_id):
    """Remove a subscriber by chat ID."""
    chat_id = str(chat_id)
    subscribers = load_subscribers()
    if chat_id in subscribers:
        del subscribers[chat_id]
        save_subscribers(subscribers)


def is_subscribed(chat_id):
    """Check if a chat ID is subscribed."""
    chat_id = str(chat_id)
    subscribers = load_subscribers()
    return chat_id in subscribers