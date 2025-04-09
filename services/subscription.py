from services.db import get_user, set_subscription_status
from datetime import datetime

def add_subscriber(telegram_id):
    """Mark user as subscribed and set timestamp."""
    user = get_user(telegram_id)
    if user and not user.is_subscribed:
        set_subscription_status(telegram_id, True)

def remove_subscriber(telegram_id):
    """Mark user as unsubscribed."""
    user = get_user(telegram_id)
    if user and user.is_subscribed:
        set_subscription_status(telegram_id, False)

def is_subscribed(telegram_id):
    """Check if the user is currently subscribed."""
    user = get_user(telegram_id)
    return user.is_subscribed if user else False