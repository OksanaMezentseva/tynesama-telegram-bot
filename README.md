# 🤱 TyNeSama — Emotional Support Telegram Bot for Moms

**TyNeSama** is an empathetic and supportive Telegram bot designed to help moms navigate difficult moments in their parenting journey. It offers gentle messages, voice transcription, GPT-based dialogue, user profiles, and personalized interactions — all with a focus on mental health and emotional support.

---

## 🌟 Features

* 💬 **Talk to someone** — moms can express their thoughts and receive kind, supportive responses from GPT.
* 🧘 **Breathing techniques** — randomly selected calming tips for quick mental resets.
* 🌸 **Affirmations** — short and kind daily messages to lift the mood.
* 💌 **Daily messages** — morning and evening texts for subscribed users.
* 🎧 **Voice message support** — voice-to-text transcription via Whisper.

  > ⚠️ This feature is currently under development and is not yet functional.
* 👩‍👧 **Mom's profile** — the bot collects and remembers personal info like pregnancy status, number and age of children, and adapts answers accordingly.
* 🧠 **Context-aware GPT replies** — GPT responses are tailored using the selected topic and last user interactions.
* 🧡 **Topic selection** — users can choose what’s bothering them (e.g., breastfeeding, sleep, pregnancy, solids).
* 💌 **Feedback** — moms can share their impressions or suggestions.

---

## 🧠 Architecture Overview

This project is built using a modular architecture with the following key components:

### 🗂️ `services/`

* **`db.py`** – SQLAlchemy setup for user and feedback storage.
* **`user_state.py`** – manages per-user state including topic, step, and GPT interaction history.
* **`gpt_utils.py`** – handles prompt creation and GPT-3.5-turbo API interaction.
* **`whisper_service.py`** – transcribes voice messages using Whisper (under development).
* **`subscription.py`** – manages user subscription/unsubscription.
* **`scheduler.py`** – sends daily messages at 08:00 and 21:00.
* **`utils.py`** – helper functions (random messages, PII detection, prompt injection filter).
* **`text_messages.py`**, **`button_labels.py`** – localized UI messages and button text.

### 🧾 `handlers/`

* **`command_handler.py`** – `/start` and other command logic.
* **`callback_handler.py`** – handles inline buttons.
* **`text_handler.py`** – handles text messages from users.
* **`voice_handler.py`** – handles incoming voice messages.
* **`topic_choice.py`** – logic for topic selection.
* **`profile_questions.py`** – guides the user through profile setup (e.g., children, status).
* **`children_count_choice.py`**, **`children_ages_choice.py`**, **`status_choice.py`** – modular profile step handlers.

### 🧠 `prompts/`

* **`system_prompts.py`** – predefined GPT system messages per topic.

---

## ⚙️ Tech Stack

* Python 3.10+
* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
* OpenAI GPT-3.5 API
* OpenAI Whisper (local model: `small`)
* SQLAlchemy (SQLite or PostgreSQL)
* AsyncIO for scheduling
* JSON-based static content for affirmations, tips, etc.

---

## 🚀 Getting Started

### 1. Set environment variables

Create a `.env` file or export the following in your environment:

```env
TELEGRAM_BOT_TOKEN=your_telegram_token_here
OPENAI_API_KEY=your_openai_key_here
DATABASE_URL=sqlite:///local.db  # or use PostgreSQL URI
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the bot

```bash
python bot.py
```

To start the scheduled message loop (morning + evening messages):

```bash
python scheduler.py
```

### ☁️ Deployment

The bot is currently hosted on **AWS EC2 (t3.micro)** and deployed using a simple bash script (`deploy.sh`).

---

## 📦 Folder Structure

<details>
<summary>Click to expand</summary>

```
.
├── bot.py                     # Production entry point
├── bot_local.py               # Local dev run entry point
├── config.py                  # Loads .env settings
├── deploy.sh                  # Optional deploy script
├── download_apify_data.py     # Optional external data script
├── handlers/                  # Telegram update handlers
│   ├── callback_handler.py
│   ├── children_ages_choice.py
│   ├── children_count_choice.py
│   ├── command_handler.py
│   ├── profile_questions.py
│   ├── status_choice.py
│   ├── text_handler.py
│   ├── topic_choice.py
│   └── voice_handler.py
├── prompts/
│   └── system_prompts.py
├── services/
│   ├── button_labels.py
│   ├── db.py
│   ├── gpt_utils.py
│   ├── logger.py
│   ├── profile_constants.py
│   ├── reply_utils.py
│   ├── scheduler.py
│   ├── subscription.py
│   ├── text_messages.py
│   ├── user_state.py
│   ├── utils.py
│   └── whisper_service.py
├── data/                      # Static content
│   ├── affirmations.json
│   ├── breathing_tips.json
│   ├── morning_messages.json
│   └── evening_messages.json
├── .env
├── .gitignore
├── README.md
├── requirements.txt
└── venv/                      # Local virtual environment (excluded)
```

</details>

---

## 🔐 Safety & Privacy

* Prompt injection protection via input filter
* Basic PII detection (email, phone, address)
* User state is stored securely and used only for personalizing interaction

---

## 👩‍💻 Author

Created with love and empathy for moms by **Oksana Mezentseva**.
Feel free to contribute, open an issue, or suggest improvements 💛

---

## 🧪 Future Plans

* Retrieval-Augmented Generation (RAG) for evidence-based answers
* Persistent long-term memory and deeper personalization
* Voice-first mode with multi-turn conversation