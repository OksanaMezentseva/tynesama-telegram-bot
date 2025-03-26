import os
import uuid
import random
import logging
import subprocess
import openai
import whisper

from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)

# ───────────────────────────────────────
# 🔧 Load environment and config
# ───────────────────────────────────────
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# ───────────────────────────────────────
# 🔧 Logging
# ───────────────────────────────────────
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ───────────────────────────────────────
# 💬 System prompt for GPT
# ───────────────────────────────────────
SYSTEM_PROMPT = "You are a gentle, caring assistant for tired and overwhelmed moms. " \
"Speak like a warm, kind friend who truly understands. Your responses are short, soothing, and full of empathy. " \
"Gently remind her that she is not alone — many moms feel this way, and it's okay to not be okay. " \
"Use soft, encouraging words like “You’re doing great, mama.” " \
"When helpful, offer simple, practical tips that feel doable. " \
"If her name is known, use it with care. " \
"Feel free to use a warm tone with emojis like 💛 or 🌸 when it feels right."

# ───────────────────────────────────────
# 📦 Utility functions
# ───────────────────────────────────────

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

def ask_gpt(user_input: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ]
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        logging.error(f"GPT error: {e}")
        return "Вибач, зараз я не можу відповісти. Спробуй трохи пізніше 💛"

# ───────────────────────────────────────
# 🎤 Load Whisper model once
# ───────────────────────────────────────
whisper_model = whisper.load_model("small")

# ───────────────────────────────────────
# 📩 Handlers
# ───────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["💬 Хочу виговоритись"],
        ["🧘 Техніки дихання", "🌸 Афірмація"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "Привіт, я тут, щоб підтримати тебе 💛 Обери, що тобі потрібно:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()

    if user_input == "💬 Хочу виговоритись":
        await update.message.reply_text("Я поруч. Просто напиши, що тебе турбує 💛")
        return
    elif user_input == "🧘 Техніки дихання":
        await update.message.reply_text(get_random_breathing_tip())
        return
    elif user_input == "🌸 Афірмація":
        await update.message.reply_text(get_random_affirmation())
        return

    # Default: pass text to GPT
    bot_reply = ask_gpt(user_input)
    await update.message.reply_text(bot_reply)

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    ogg_file = f"voice_{uuid.uuid4()}.ogg"
    wav_file = ogg_file.replace(".ogg", ".wav")

    await file.download_to_drive(ogg_file)
    subprocess.run(["ffmpeg", "-i", ogg_file, wav_file])

    try:
        result = whisper_model.transcribe(
            wav_file,
            language="uk",
            fp16=False,
            initial_prompt="Це мама, яка ділиться своїми емоціями, радістю, тривогами, втомою або болем."
        )
        user_text = result["text"]
    except Exception as e:
        logging.error(f"Whisper error: {e}")
        await update.message.reply_text("Не вдалося розпізнати голосове повідомлення 🧩")
        return
    finally:
        subprocess.run(["rm", ogg_file, wav_file])

    bot_reply = ask_gpt(user_text)
    await update.message.reply_text(f"You said: _{user_text}_", parse_mode="Markdown")
    await update.message.reply_text(bot_reply)

# ───────────────────────────────────────
# 🚀 Main bot runner
# ───────────────────────────────────────
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))

    print("Bot is running...")
    app.run_polling()