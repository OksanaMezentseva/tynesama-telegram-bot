import logging
import time
from telegram import (
    Update, ReplyKeyboardMarkup,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import ContextTypes

from services.db import add_user, get_user
from services.utils import send_support_buttons
from services.reply_utils import update_reply_keyboard, get_main_keyboard
from services.subscription import add_subscriber, remove_subscriber, is_subscribed
from services.user_state import UserStateManager
from handlers.profile_questions import PROFILE_QUESTIONS

from services.button_labels import (
    BTN_PROFILE_INLINE,
)

from services.text_messages import (
    GREETING_TEXT,
    SUBSCRIBED_TEXT,
    ALREADY_SUBSCRIBED_TEXT,
    UNSUBSCRIBED_TEXT,
    ALREADY_UNSUBSCRIBED_TEXT,
    PROFILE_MESSAGE,
)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles /start command: registers the user, initializes state,
    sends greeting and main menu with inline profile setup button.
    """
    t0 = time.time()
    logging.info("📩 /start command received")

    chat_id = str(update.effective_chat.id)

    try:
        # Add user to DB if not already present
        t_add = time.time()
        add_user(chat_id)
        logging.info(f"👤 add_user() completed in {time.time() - t_add:.2f}s")

        # Initialize user state
        t_state = time.time()
        state = UserStateManager(chat_id)
        state.set_step("started")
        logging.info(f"🧠 UserStateManager initialized in {time.time() - t_state:.2f}s")

        # Send greeting with main keyboard
        reply_markup = get_main_keyboard()
        await update.message.reply_text(GREETING_TEXT, reply_markup=reply_markup)

        # Inline button to edit/fill profile
        inline_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(BTN_PROFILE_INLINE, callback_data="edit_profile")]
        ])
        await update.message.reply_text(PROFILE_MESSAGE, reply_markup=inline_keyboard)

        logging.info(f"📨 Replies sent in {time.time() - t_state:.2f}s")

    except Exception as e:
        logging.error(f"❌ Error in start_command: {e}")

    logging.info(f"✅ /start handled in total {time.time() - t0:.2f}s")


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Subscribes the user to daily messages.
    """
    chat_id = str(update.effective_chat.id)

    if not is_subscribed(chat_id):
        add_subscriber(chat_id)
        await update_reply_keyboard(update, context, message=SUBSCRIBED_TEXT)
    else:
        await update_reply_keyboard(update, context, message=ALREADY_SUBSCRIBED_TEXT)


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Unsubscribes the user from daily messages.
    """
    chat_id = str(update.effective_chat.id)

    if is_subscribed(chat_id):
        remove_subscriber(chat_id)
        await update_reply_keyboard(update, context, message=UNSUBSCRIBED_TEXT)
    else:
        await update_reply_keyboard(update, context, message=ALREADY_UNSUBSCRIBED_TEXT)


async def support_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows inline support options (e.g., donation, links).
    """
    await send_support_buttons(update, context)


async def test_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Admin-only: tests DB connectivity and user data.
    """
    telegram_id = str(update.effective_chat.id)

    if telegram_id != "790924168":
        logging.warning(f"⛔ Unauthorized access attempt to /testdb by {telegram_id}")
        await update.message.reply_text("⛔️ You are not allowed to run this command.")
        return

    add_user(telegram_id)
    user = get_user(telegram_id)

    if user:
        await update.message.reply_text(
            f"✅ DB works!\nUser ID: {user.telegram_id}\nSubscribed: {user.is_subscribed}"
        )
    else:
        await update.message.reply_text("❌ DB not working")


async def handle_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows the user's current profile and provides inline button to edit it.
    """
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from services.button_labels import BTN_PROFILE_INLINE

    telegram_id = str(update.effective_user.id)
    state = UserStateManager(telegram_id)

    # Save current step before editing so we can return after
    state.set("previous_menu", state.get_step())

    # Load profile data
    profile_data = state.get_profile_data()
    profile_text = "📋 *Твій профіль:*\n\n"
    filled = False

    for q in PROFILE_QUESTIONS:
        key = q["key"]
        label = q["question"]
        value = profile_data.get(key)

        if value:
            # Format list values as comma-separated
            if isinstance(value, list):
                value = ", ".join(str(v) for v in value)
            profile_text += f"▫️ *{label}*\n{value}\n\n"
            filled = True

    if not filled:
        profile_text += "_Профіль ще не заповнено._"

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(BTN_PROFILE_INLINE, callback_data="edit_profile")]
    ])

    await update.message.reply_text(profile_text, parse_mode="Markdown", reply_markup=keyboard)
