# 🤱 TyNeSama — Emotional Support Telegram Bot for Moms

**TyNeSama** is an empathetic and supportive Telegram bot designed to help moms navigate difficult moments in their parenting journey. It offers gentle messages, voice transcription, GPT-based dialogue, and personalized interactions — all with a focus on mental health and emotional support.

---

## 🌟 Features

* 💬 **Talk to someone** — moms can express their thoughts and receive kind, supportive responses from GPT.
* 🧘 **Breathing techniques** — randomly selected calming tips for quick mental resets.
* 🌸 **Affirmations** — short and kind daily messages to lift the mood.
* 💌 **Daily messages** — morning and evening texts for subscribed users.
* 🎧 **Voice message support** — voice-to-text transcription via Whisper. > ⚠️ This feature is currently under development and is not yet functional.
* 🧡 **Topic selection** — users can choose what’s bothering them (breastfeeding, sleep, pregnancy, solids).
* 💌 **Feedback** — moms can share their impressions or suggestions.

---

## 🧠 Architecture Overview

This project is built using a modular architecture with the following key components:

### 🗂️ `services/`

* **`db.py`** – SQLAlchemy setup for user/feedback management.
* **`user_state.py`** – stores and manages per-user state (topic, step, GPT history).
* **`whisper_service.py`** – voice message transcription via OpenAI Whisper.
* **`gpt_utils.py`** – GPT-3.5-turbo integration with short-term memory per topic.
* **`subscription.py`** – subscription logic (subscribe/unsubscribe).
* **`scheduler.py`** – sends daily messages at 08:00 and 21:00 to subscribed users.
* **`utils.py`** – helper functions for random messages, PII and prompt injection protection.

### 🧾 `text_messages.py` and `button_labels.py`

Contain all UI text and button labels to support clear interaction and localization.

---

## ⚙️ Tech Stack

* Python 3.10+
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* OpenAI GPT-3.5 API
* OpenAI Whisper (local model: `small`)
* SQLAlchemy (SQLite or Postgres, configurable)
* AsyncIO (for scheduling daily messages)
* JSON-based content storage for affirmations and tips

---

## 🚀 Getting Started

### 1. Set environment variables

Create a `.env` file or export them in your environment:

```env
TELEGRAM_BOT_TOKEN=your_telegram_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=sqlite:///local.db  # or PostgreSQL URI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the bot

```bash
python bot.py
```

To start the daily scheduler:

```bash
python scheduler.py
```

---

## 📦 Folder Structure

<details>
<summary>Click to expand</summary>

```
.
├── bot.py                     # Production entry point for the bot
├── bot_local.py               # Local/dev bot entry point
├── config.py                  # Loads env config values
├── deploy.sh                  # Deployment script (e.g. for Render)
├── download_apify_data.py     # Data fetcher from external source (Apify)
├── handlers/                  # Telegram handlers by type
│   ├── callback_handler.py
│   ├── command_handler.py
│   ├── profile_questions.py   # Handles user profile Q&A flow
│   ├── text_handler.py
│   └── voice_handler.py
├── prompts/
│   └── system_prompts.py      # System messages for GPT by topic
├── services/                  # Main business logic and shared services
│   ├── button_labels.py
│   ├── db.py
│   ├── gpt_utils.py
│   ├── logger.py
│   ├── profile_constants.py
│   ├── reply_utils.py
│   ├── scheduler.py
│   ├── subscription.py
│   ├── text_messages.py
│   ├── topic_choice.py
│   ├── user_state.py
│   ├── utils.py
│   └── whisper_service.py
├── data/                      # JSON-based static content
│   ├── affirmations.json
│   ├── breathing_tips.json
│   ├── morning_messages.json
│   └── evening_messages.json
├── .env                       # Environment variables
├── .gitignore
├── README.md
├── requirements.txt
└── venv/                      # (local virtual environment)
```

</details>

---

## 🔐 Safety & Privacy

* Prompt injection protection via pattern matching
* Basic PII detection (email, phone number, address)
* All interactions are stored locally per user and not shared

---

## 👩‍💻 Author

Created with care and empathy for moms by Oksana Mezentseva.
Feel free to contribute or suggest improvements!

---

## 🧪 Future Plans

* RAG integration for evidence-based recommendations
* Long-term user memory and personalization
* Voice-based full conversation mode
