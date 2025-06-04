from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from services.user_state import UserStateManager
from handlers.profile_questions import send_next_profile_question

# Options for children count
CHILDREN_COUNT_CHOICES = {
    "1": "1",
    "2": "2",
    "3_plus": "3+"
}

def build_children_count_keyboard(selected: str = None) -> InlineKeyboardMarkup:
    buttons = []
    for key, label in CHILDREN_COUNT_CHOICES.items():
        prefix = "✅ " if key == selected else ""
        buttons.append([InlineKeyboardButton(f"{prefix}{label}", callback_data=f"children_count_choice:{key}")])
    return InlineKeyboardMarkup(buttons)

async def send_children_count_keyboard(chat_id, context, state):
    selected = state.get_profile_data().get("children_count_key")
    keyboard = build_children_count_keyboard(selected)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Скільки у тебе діток? Обери один варіант 💛",
        reply_markup=keyboard
    )

async def handle_children_count_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    state = UserStateManager(str(query.from_user.id))
    profile_data = state.get_profile_data()

    data = query.data
    if data.startswith("children_count_choice:"):
        selected_key = data.split(":")[1]
        selected_label = CHILDREN_COUNT_CHOICES[selected_key]

        # Save both label and key
        profile_data["children_count"] = selected_label
        profile_data["children_count_key"] = selected_key

        state.set_profile_data(profile_data)
        state.increment_profile_progress()

        await query.edit_message_reply_markup(reply_markup=None)
        await send_next_profile_question(update.effective_message, context, state)