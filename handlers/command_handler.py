from telegram import Update, ReplyKeyboardMarkup
from services.db import add_user, get_user, update_user_state
from telegram.ext import ContextTypes, CommandHandler
from services.subscription import add_subscriber, remove_subscriber, is_subscribed
from services.user_state import UserStateManager
from services.button_labels import (
    BTN_TALK,
    BTN_BREATHING,
    BTN_AFFIRMATION,
    BTN_SUBSCRIBE,
    BTN_UNSUBSCRIBE,
    BTN_TOPICS,
    BTN_FEEDBACK
)
from services.text_messages import (
    GREETING_TEXT,
    SUBSCRIBED_TEXT,
    ALREADY_SUBSCRIBED_TEXT,
    UNSUBSCRIBED_TEXT,
    ALREADY_UNSUBSCRIBED_TEXT,
    DEFAULT_UPDATE_TEXT
)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initial /start command with greeting and keyboard."""
    chat_id = str(update.effective_chat.id)

    # Add user if not exists
    add_user(chat_id)

    # Update user_state: step = started
    state = UserStateManager(chat_id)
    state.set_step("started")

    await update_reply_keyboard(update, context, message=GREETING_TEXT)


async def update_reply_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE, message: str = DEFAULT_UPDATE_TEXT):
    """Update reply keyboard based on subscription status."""
    chat_id = str(update.effective_chat.id)

    if is_subscribed(chat_id):
        keyboard = [
            [BTN_TALK, BTN_TOPICS],
            [BTN_BREATHING, BTN_AFFIRMATION],
            [BTN_FEEDBACK, BTN_UNSUBSCRIBE]
        ]
    else:
        keyboard = [
            [BTN_BREATHING, BTN_AFFIRMATION],
            [BTN_TOPICS],
            [BTN_FEEDBACK, BTN_SUBSCRIBE]
        ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        message,
        reply_markup=reply_markup
    )


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user subscription."""
    chat_id = str(update.effective_chat.id)

    if not is_subscribed(chat_id):
        add_subscriber(chat_id)
        await update_reply_keyboard(update, context, message=SUBSCRIBED_TEXT)
    else:
        await update_reply_keyboard(update, context, message=ALREADY_SUBSCRIBED_TEXT)


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user unsubscription."""
    chat_id = str(update.effective_chat.id)

    if is_subscribed(chat_id):
        remove_subscriber(chat_id)
        await update_reply_keyboard(update, context, message=UNSUBSCRIBED_TEXT)
    else:
        await update_reply_keyboard(update, context, message=ALREADY_UNSUBSCRIBED_TEXT)


async def test_db(update: Update, context: ContextTypes.DEFAULT_TYPE):
    telegram_id = str(update.effective_chat.id)

    # Allow only your ID to run this command
    if telegram_id != "790924168":
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