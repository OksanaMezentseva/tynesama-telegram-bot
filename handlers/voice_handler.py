import uuid
import subprocess
import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.whisper_service import transcribe_voice
from services.gpt_service import ask_gpt
from services.subscription import is_subscribed

# --- Message constants ---
NOT_SUBSCRIBED_TEXT = "Ця функція доступна лише після підписки. Натисни /subscribe 💛"
WHISPER_ERROR_TEXT = "Не вдалося розпізнати голосове повідомлення 🧩"
RECOGNIZED_PREFIX = "You said: _"

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    # Check subscription status
    if not is_subscribed(chat_id):
        await update.message.reply_text(NOT_SUBSCRIBED_TEXT)
        return

    # Download and convert the voice message
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    ogg_file = f"voice_{uuid.uuid4()}.ogg"
    wav_file = ogg_file.replace(".ogg", ".wav")

    await file.download_to_drive(ogg_file)
    subprocess.run(["ffmpeg", "-i", ogg_file, wav_file])

    try:
        # Transcribe voice to text
        user_text = transcribe_voice(wav_file)
    except Exception as e:
        logging.error(f"Whisper error: {e}")
        await update.message.reply_text(WHISPER_ERROR_TEXT)
        return
    finally:
        # Clean up temporary files
        subprocess.run(["rm", ogg_file, wav_file])

    # Generate response from GPT
    bot_reply = ask_gpt(user_text)
    await update.message.reply_text(f"{RECOGNIZED_PREFIX}{user_text}_", parse_mode="Markdown")
    await update.message.reply_text(bot_reply)