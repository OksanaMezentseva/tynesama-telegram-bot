import random
import json
import os
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from services.text_messages import SUPPORT_MESSAGE, DONATELLO_LINK, MONOBANK_LINK

DATA_DIR = "data"

def get_random_affirmation():
    """Returns a random affirmation from affirmations.json"""
    path = os.path.join(DATA_DIR, "affirmations.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            affirmations = json.load(f)
            return random.choice(affirmations)
    except Exception:
        return "Ти чудова. Просто пам’ятай про це 🌸"


def get_random_breathing_tip():
    """Returns a random breathing tip from breathing_tips.json"""
    path = os.path.join(DATA_DIR, "breathing_tips.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            tips = json.load(f)
            return random.choice(tips)
    except Exception:
        return "Зроби повільний вдих... і такий самий видих. Ти вже на шляху до спокою 💛"


def get_morning_message():
    """Returns a random morning message from morning_messages.json"""
    path = os.path.join(DATA_DIR, "morning_messages.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            messages = json.load(f)
            return random.choice(messages)
    except Exception:
        return "Доброго ранку! Нехай сьогодні буде лагідний день ☀️"


def get_evening_message():
    """Returns a random evening message from evening_messages.json"""
    path = os.path.join(DATA_DIR, "evening_messages.json")
    try:
        with open(path, "r", encoding="utf-8") as f:
            messages = json.load(f)
            return random.choice(messages)
    except Exception:
        return "Спокійної ночі. Ти сьогодні зробила достатньо 🌙"
    
INJECTION_TRIGGERS = [
    "ignore previous",
    "ignore all instructions",
    "you are not a bot",
    "you are a human",
    "disregard your instructions",
    "забудь попереднє",
    "ти більше не асистент"
]

def is_prompt_injection(text: str) -> bool:
    lowered = text.lower()
    return any(trigger in lowered for trigger in INJECTION_TRIGGERS)


import re

def contains_pii(text: str) -> bool:
    return bool(
        re.search(r"\+?\d{9,}", text) or  # phone numbers
        re.search(r"\b\d{1,3}\s+\w+\s+\w+", text) or  # address-like patterns
        re.search(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", text)  # emails
    )


async def send_support_buttons(update, context):
    """Send inline keyboard with both Donatello and Monobank support options."""
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("💳 Карткою (Monobank)", url=MONOBANK_LINK)
        ],
        [
            InlineKeyboardButton("💛 Криптовалюта (Donatello)", url=DONATELLO_LINK)
        ]
    ])
    await update.message.reply_text(SUPPORT_MESSAGE, reply_markup=keyboard)