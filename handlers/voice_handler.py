import uuid
import subprocess
import logging
import os
import openai
import re
from telegram import Update
from telegram.ext import ContextTypes
from services.whisper_service import transcribe_voice
from services.subscription import is_subscribed
from services.user_state import UserStateManager
from services.gpt_utils import ask_gpt_with_history
from services.utils import is_prompt_injection, contains_pii
from services.text_messages import (
    WHISPER_ERROR_TEXT,
    RECOGNIZED_PREFIX,
    INJECTION_BLOCK_TEXT,
    PII_WARNING_TEXT,
)

openai.api_key = os.getenv("OPENAI_API_KEY")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_id_str = str(chat_id)
    logging.info(f"🎹 Voice message received from {chat_id_str}")

    state = UserStateManager(chat_id_str)

    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    ogg_file = f"voice_{uuid.uuid4()}.ogg"
    wav_file = ogg_file.replace(".ogg", ".wav")

    logging.info("⬇️ Downloading voice...")
    await file.download_to_drive(ogg_file)

    logging.info("🎛 Converting OGG to WAV...")
    subprocess.run(["ffmpeg", "-i", ogg_file, wav_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        logging.info("🧠 Transcribing audio...")
        user_text = transcribe_voice(wav_file)
        logging.info(f"📝 Transcribed text: {user_text}")
    except Exception as e:
        logging.warning(f"❌ Whisper error for user {chat_id_str}: {e}")
        await update.message.reply_text(WHISPER_ERROR_TEXT)
        return
    finally:
        subprocess.run(["rm", ogg_file, wav_file])

    if not user_text.strip():
        await update.message.reply_text("🔇 Не вдалося розпізнати голос. Спробуй ще раз 🙏")
        return

    if is_prompt_injection(user_text):
        await update.message.reply_text(INJECTION_BLOCK_TEXT)
        return

    if contains_pii(user_text):
        await update.message.reply_text(PII_WARNING_TEXT)
        return

    try:
        bot_reply = ask_gpt_with_history(state, user_text)
        await update.message.reply_text(
            f"{RECOGNIZED_PREFIX}{user_text}_\n\n{bot_reply}",
            parse_mode="Markdown"
        )
    except Exception as e:
        logging.warning(f"⚠️ GPT error for voice input from {chat_id_str}: {e}")
        await update.message.reply_text("⚠️ Щось пішло не так. Спробуй ще раз пізніше.")