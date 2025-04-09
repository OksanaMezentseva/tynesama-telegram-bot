import random
import json
import os

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