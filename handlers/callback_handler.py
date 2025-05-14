import logging
from telegram import Update
from telegram.ext import ContextTypes
from services.user_state import UserStateManager
from handlers.profile_questions import send_next_profile_question

async def handle_profile_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles inline callback for profile editing.
    Resets profile state and initiates the profile question flow.
    """
    query = update.callback_query
    await query.answer()
    logging.info(f"📩 Callback received: {query.data}")

    if query.data != "edit_profile":
        logging.warning(f"⚠️ Unknown callback_data received: {query.data}")
        await query.message.reply_text("Ця кнопка поки що не працює.")
        return

    telegram_id = str(query.from_user.id)
    state = UserStateManager(telegram_id)

    # Preserve previous menu context for redirect after profile completion
    previous_step = state.get_step()
    state.set("previous_menu", previous_step)

    # Reset profile state
    state.set_step("profile_q0")
    state.set("profile_progress", 0)
    state.set("profile_data", {})

    logging.info(f"👤 Starting profile setup for user {telegram_id}")

    message = query.message
    await send_next_profile_question(message, context, state)