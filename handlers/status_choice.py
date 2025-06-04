from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from services.user_state import UserStateManager
from handlers.profile_questions import send_next_profile_question

STATUS_CHOICES = {
    "pregnant": "🤰 Вагітна",
    "has_children": "👶 Маю дітей",
    "none": "🚫 Немає дітей, не вагітна"
}

def build_status_keyboard(selected: str = None):
    buttons = []
    for key, label in STATUS_CHOICES.items():
        prefix = "✅ " if key == selected else ""
        buttons.append([InlineKeyboardButton(f"{prefix}{label}", callback_data=f"status_choice:{key}")])
    return InlineKeyboardMarkup(buttons)

async def send_status_keyboard(chat_id, context, state):
    selected = state.get_profile_data().get("status_key")
    keyboard = build_status_keyboard(selected)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Обери, яка в тебе ситуація зараз 💛",
        reply_markup=keyboard
    )

async def handle_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    state = UserStateManager(str(query.from_user.id))
    profile_data = state.get_profile_data()

    data = query.data
    if data.startswith("status_choice:"):
        selected_key = data.split(":")[1]
        selected_label = STATUS_CHOICES[selected_key]

        # Save both label and key
        profile_data["status"] = selected_label
        profile_data["status_key"] = selected_key

        state.set_profile_data(profile_data)
        state.increment_profile_progress()
        await query.edit_message_reply_markup(reply_markup=None)
        await send_next_profile_question(update.effective_message, context, state)
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from services.user_state import UserStateManager
from handlers.profile_questions import send_next_profile_question

STATUS_CHOICES = {
    "pregnant": "🤰 Вагітна",
    "has_children": "👶 Маю дітей",
    "none": "🚫 Немає дітей, не вагітна"
}

def build_status_keyboard(selected: str = None):
    buttons = []
    for key, label in STATUS_CHOICES.items():
        prefix = "✅ " if key == selected else ""
        buttons.append([InlineKeyboardButton(f"{prefix}{label}", callback_data=f"status_choice:{key}")])
    return InlineKeyboardMarkup(buttons)

async def send_status_keyboard(chat_id, context, state):
    selected = state.get_profile_data().get("status_key")
    keyboard = build_status_keyboard(selected)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Обери, яка в тебе ситуація зараз 💛",
        reply_markup=keyboard
    )

async def handle_status_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    state = UserStateManager(str(query.from_user.id))
    profile_data = state.get_profile_data()

    data = query.data
    if data.startswith("status_choice:"):
        selected_key = data.split(":")[1]
        selected_label = STATUS_CHOICES[selected_key]

        # Save both label and key
        profile_data["status"] = selected_label
        profile_data["status_key"] = selected_key
        state.set_profile_data(profile_data)

        if selected_key in {"pregnant", "none"}:
            # Skip next two questions: children_count and children_ages
            current_progress = state.get("profile_progress", 0)
            state.set("profile_progress", current_progress + 3)
        else:
            # Proceed to next question normally
            state.increment_profile_progress()

        await query.edit_message_reply_markup(reply_markup=None)
        await send_next_profile_question(update.effective_message, context, state)