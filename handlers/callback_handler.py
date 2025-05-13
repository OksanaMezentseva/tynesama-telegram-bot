import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.user_state import UserStateManager
from handlers.profile_questions import send_next_profile_question

async def handle_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles inline button clicks with callback_data.
    Currently supports 'edit_profile' to start profile setup flow.
    """
    query = update.callback_query
    await query.answer()

    telegram_id = str(query.from_user.id)
    state = UserStateManager(telegram_id)

    if query.data == "edit_profile":
        # Initialize the profile setup state
        state.set_step("profile_q0")
        state.set("profile_progress", 0)  # index in PROFILE_QUESTIONS
        state.set("profile_data", {})     # temporary profile storage

        logging.info(f"👤 Starting profile setup for user {telegram_id}")
        await send_next_profile_question(update, context, state)

    else:
        logging.warning(f"⚠️ Unknown callback_data received: {query.data}")
        await query.message.reply_text("Ця кнопка поки що не працює.")