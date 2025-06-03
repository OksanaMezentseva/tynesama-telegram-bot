from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from services.user_state import UserStateManager
from handlers.profile_questions import send_next_profile_question

AGE_CHOICES = [
    "0–6 міс",
    "7–12 міс",
    "1–3 роки",
    "4–7 років",
    "8+ років"
]

def build_age_keyboard(selected):
    """Build inline keyboard with toggleable age ranges."""
    buttons = []
    for age in AGE_CHOICES:
        prefix = "✅" if age in selected else "⬜️"
        buttons.append([InlineKeyboardButton(f"{prefix} {age}", callback_data=f"toggle_age:{age}")])
    buttons.append([InlineKeyboardButton("✅ Зберегти вибір", callback_data="save_ages")])
    return InlineKeyboardMarkup(buttons)

async def send_children_ages_keyboard(chat_id, context, state):
    selected = state.get_profile_data().get("children_ages", [])
    keyboard = build_age_keyboard(selected)
    await context.bot.send_message(
        chat_id=chat_id,
        text="У якому віковому періоді зараз твої дітки? Можна обрати кілька 💛",
        reply_markup=keyboard
    )

async def handle_children_ages_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    state = UserStateManager(str(query.from_user.id))

    data = query.data
    profile_data = state.get_profile_data()
    selected = set(profile_data.get("children_ages", []))

    if data.startswith("toggle_age:"):
        age = data.split(":")[1]
        if age in selected:
            selected.remove(age)
        else:
            selected.add(age)

        profile_data["children_ages"] = list(selected)
        state.set_profile_data(profile_data)
        await query.edit_message_reply_markup(reply_markup=build_age_keyboard(selected))

    elif data == "save_ages":
        if not selected:
            await query.answer("Будь ласка, обери хоча б один період 🙏", show_alert=True)
            return

        await query.edit_message_reply_markup(reply_markup=None)
        state.set_profile_data(profile_data)
        state.increment_profile_progress()
        await send_next_profile_question(update.effective_message, context, state)
