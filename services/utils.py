import random
import json

def get_random_affirmation():
    try:
        with open("affirmations.txt", "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
            return random.choice(lines)
    except Exception:
        return "Ти чудова. Просто пам’ятай про це 🌸"


def get_random_breathing_tip():
    try:
        with open("breathing.txt", "r", encoding="utf-8") as f:
            tips = [line.strip() for line in f if line.strip()]
            return random.choice(tips)
    except Exception:
        return "Зроби повільний вдих... і такий самий видих. Ти вже на шляху до спокою 💛"

def get_morning_message():
    try:
        with open("morning_messages.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
            return random.choice(messages)
    except Exception:
        return "Доброго ранку! Нехай сьогодні буде лагідний день ☀️"


def get_evening_message():
    try:
        with open("evening_messages.json", "r", encoding="utf-8") as f:
            messages = json.load(f)
            return random.choice(messages)
    except Exception:
        return "Спокійної ночі. Ти сьогодні зробила достатньо 🌙"