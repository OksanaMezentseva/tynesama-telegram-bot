import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from services.utils import get_random_affirmation, get_random_breathing_tip
from services.subscription import is_subscribed
from services.user_state import UserStateManager
from services.db import save_feedback
from handlers.command_handler import subscribe_command, unsubscribe_command
from services.gpt_utils import ask_gpt_with_history
from services.button_labels import (
    BTN_TALK, BTN_BREATHING, BTN_AFFIRMATION, BTN_SUBSCRIBE, BTN_UNSUBSCRIBE,
    BTN_TOPICS, BTN_SOLIDS, BTN_BREASTFEEDING, BTN_SLEEP, BTN_PREGNANCY, BTN_BACK, BTN_FEEDBACK
)
from services.text_messages import (
    SYSTEM_PROMPT, SYSTEM_PROMPT_BREASTFEEDING, SYSTEM_PROMPT_SOLIDS,
    SYSTEM_PROMPT_PREGNANCY, SYSTEM_PROMPT_SLEEP,
    MSG_SUBSCRIBE_REQUIRED, MSG_READY_TO_LISTEN, MSG_CHOOSE_TOPIC,
    LOGIC_BACK_TO_MAIN_MENU, REPLY_BREASTFEEDING, REPLY_SOLIDS,
    REPLY_PREGNANCY, REPLY_SLEEP, MSG_FEEDBACK_THANKS, MSG_FEEDBACK_PROMPT
)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


async def choose_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [BTN_BREASTFEEDING, BTN_SOLIDS],
        [BTN_SLEEP, BTN_PREGNANCY],
        [BTN_BACK]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(MSG_CHOOSE_TOPIC, reply_markup=reply_markup)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    chat_id = update.effective_chat.id
    chat_id_str = str(chat_id)
    state = UserStateManager(chat_id_str)

    # Handle feedback
    if state.get_step() == "waiting_for_feedback":
        save_feedback(chat_id_str, user_input)
        state.set_step("started")
        await update.message.reply_text(MSG_FEEDBACK_THANKS)
        if ADMIN_CHAT_ID:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"\U0001F4AC Відгук від {chat_id_str}:\n{user_input}")
        return

    # Subscription actions
    if user_input == BTN_SUBSCRIBE:
        await subscribe_command(update, context)
        return

    if user_input == BTN_UNSUBSCRIBE:
        await unsubscribe_command(update, context)
        return

    # Feedback prompt
    if user_input == BTN_FEEDBACK:
        state.set_step("waiting_for_feedback")
        await update.message.reply_text(MSG_FEEDBACK_PROMPT)
        return

    # Affirmation / Breathing
    if user_input == BTN_AFFIRMATION:
        await update.message.reply_text(get_random_affirmation())
        return

    if user_input == BTN_BREATHING:
        await update.message.reply_text(get_random_breathing_tip())
        return

    # Talk with GPT
    if user_input == BTN_TALK:
        if not is_subscribed(chat_id):
            await update.message.reply_text(MSG_SUBSCRIBE_REQUIRED)
            return
        state.set_step("waiting_for_gpt_question")
        await update.message.reply_text(MSG_READY_TO_LISTEN)
        return

    # Topics
    if user_input == BTN_TOPICS:
        state.set_step("choosing_topic")
        await choose_topic_handler(update, context)
        return

    if user_input == BTN_BACK:
        from handlers.command_handler import update_reply_keyboard
        state.set_step("started")
        state.set("topic", None)
        await update_reply_keyboard(update, context, message=LOGIC_BACK_TO_MAIN_MENU)
        return

    # Topic selection
    topics_map = {
        BTN_BREASTFEEDING: ("breastfeeding", REPLY_BREASTFEEDING),
        BTN_SOLIDS: ("solids", REPLY_SOLIDS),
        BTN_PREGNANCY: ("pregnancy", REPLY_PREGNANCY),
        BTN_SLEEP: ("sleep", REPLY_SLEEP)
    }

    if user_input in topics_map:
        topic_key, reply = topics_map[user_input]
        state.set("topic", topic_key)
        await update.message.reply_text(reply)
        return

    # GPT flow
    if not is_subscribed(chat_id):
        await update.message.reply_text(MSG_SUBSCRIBE_REQUIRED)
        return

    topic = state.get("topic")
    system_prompt = {
        "breastfeeding": SYSTEM_PROMPT_BREASTFEEDING,
        "solids": SYSTEM_PROMPT_SOLIDS,
        "pregnancy": SYSTEM_PROMPT_PREGNANCY,
        "sleep": SYSTEM_PROMPT_SLEEP
    }.get(topic, SYSTEM_PROMPT)

    try:
        bot_reply = ask_gpt_with_history(state, user_input, system_prompt)
        await update.message.reply_text(bot_reply)
    except Exception as e:
        await update.message.reply_text("⚠️ Щось пішло не так. Спробуй ще раз пізніше.")
        logging.warning(f"⚠️ GPT error for {chat_id_str}: {e}")