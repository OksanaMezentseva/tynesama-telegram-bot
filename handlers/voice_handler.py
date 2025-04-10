import uuid
import subprocess
import logging
import os
import openai
from telegram import Update
from telegram.ext import ContextTypes
from services.whisper_service import transcribe_voice
from services.subscription import is_subscribed
from services.user_state import UserStateManager
from services.text_messages import (
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_BREASTFEEDING,
    SYSTEM_PROMPT_SOLIDS,
    SYSTEM_PROMPT_PREGNANCY,
    SYSTEM_PROMPT_SLEEP
)

# --- Message constants ---
NOT_SUBSCRIBED_TEXT = "Ця функція доступна лише після підписки. Натисни /subscribe 💛"
WHISPER_ERROR_TEXT = "Не вдалося розпізнати голосове повідомлення 🧩"
RECOGNIZED_PREFIX = "You said: _"

openai.api_key = os.getenv("OPENAI_API_KEY")

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    chat_id_str = str(chat_id)
    logging.info(f"🎙 Voice message received from {chat_id_str}")

    # Check subscription status
    if not is_subscribed(chat_id):
        await update.message.reply_text(NOT_SUBSCRIBED_TEXT)
        return

    state = UserStateManager(chat_id_str)
    topic = state.get("topic")

    # Determine prompt by topic
    if topic == "breastfeeding":
        system_prompt = SYSTEM_PROMPT_BREASTFEEDING
    elif topic == "solids":
        system_prompt = SYSTEM_PROMPT_SOLIDS
    elif topic == "pregnancy":
        system_prompt = SYSTEM_PROMPT_PREGNANCY
    elif topic == "sleep":
        system_prompt = SYSTEM_PROMPT_SLEEP
    else:
        system_prompt = SYSTEM_PROMPT

    # Download and convert voice file
    voice = update.message.voice
    file = await context.bot.get_file(voice.file_id)

    ogg_file = f"voice_{uuid.uuid4()}.ogg"
    wav_file = ogg_file.replace(".ogg", ".wav")

    await file.download_to_drive(ogg_file)
    subprocess.run(["ffmpeg", "-i", ogg_file, wav_file], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    try:
        user_text = transcribe_voice(wav_file)
    except Exception as e:
        logging.warning(f"❌ Whisper error for user {chat_id_str}: {e}")
        await update.message.reply_text(WHISPER_ERROR_TEXT)
        return
    finally:
        subprocess.run(["rm", ogg_file, wav_file])

    # GPT interaction
    history = state.get_gpt_history(topic)
    messages = [{"role": "system", "content": system_prompt}]
    for pair in history[-3:]:
        messages.append({"role": "user", "content": pair["question"]})
        messages.append({"role": "assistant", "content": pair["reply"]})
    messages.append({"role": "user", "content": user_text})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        bot_reply = response["choices"][0]["message"]["content"]
        state.add_gpt_interaction(user_text, bot_reply)

        await update.message.reply_text(f"{RECOGNIZED_PREFIX}{user_text}_", parse_mode="Markdown")
        await update.message.reply_text(bot_reply)

    except Exception as e:
        logging.warning(f"⚠️ GPT error for voice input from {chat_id_str}: {e}")
        await update.message.reply_text("⚠️ Щось пішло не так. Спробуй ще раз пізніше.")