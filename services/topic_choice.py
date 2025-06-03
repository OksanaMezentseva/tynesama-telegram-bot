from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from services.user_state import UserStateManager
from handlers.profile_questions import send_next_profile_question

TOPIC_CHOICES = {
    "breastfeeding": "🤱 Грудне вигодовування",
    "solids": "🥣 Прикорм",
    "sleep": "👼 Сон малюка",
    "pregnancy": "🤰 Вагітність",
    "development": "🧠 Розвиток дитини",
    "tantrums": "😡 Істерики, емоції",
    "mental_health": "💛 Емоції мами",
    "partner_support": "💬 Підтримка з боку партнера",
    "routine": "⏰ Денний режим",
    "teething": "🦷 Прорізування зубів"
}

def build_topic_keyboard(selected):
    buttons = []
    for key, label in TOPIC_CHOICES.items():
        prefix = "✅" if key in selected else "⬜️"
        buttons.append([InlineKeyboardButton(f"{prefix} {label}", callback_data=f"toggle_topic:{key}")])
    buttons.append([InlineKeyboardButton("✅ Зберегти вибір", callback_data="save_topics")])
    return InlineKeyboardMarkup(buttons)

async def send_topic_selection_keyboard(chat_id, context, state):
    selected = state.get("preferred_topics", [])
    keyboard = build_topic_keyboard(selected)
    await context.bot.send_message(
        chat_id=chat_id,
        text="Які теми тобі цікаві? Можна обрати кілька:",
        reply_markup=keyboard
    )

async def handle_topic_callback(update, context):
    query = update.callback_query
    await query.answer()
    state = UserStateManager(str(query.from_user.id))

    data = query.data
    profile_data = state.get("profile_data", {})
    selected = set(profile_data.get("preferred_topics", []))

    if data.startswith("toggle_topic:"):
        topic = data.split(":")[1]
        if topic not in TOPIC_CHOICES:
            return

        if topic in selected:
            selected.remove(topic)
        else:
            selected.add(topic)

        profile_data["preferred_topics"] = list(selected)
        state.set("profile_data", profile_data)
        await query.edit_message_reply_markup(reply_markup=build_topic_keyboard(selected))

    elif data == "save_topics":
        if not selected:
            await query.answer("Будь ласка, обери хоча б одну тему 🙏", show_alert=True)
            return

        await query.edit_message_reply_markup(reply_markup=None)

        profile_data["preferred_topics"] = list(selected)
        state.set("profile_data", profile_data)
        state.set("profile_progress", state.get("profile_progress", 0) + 1)

        await send_next_profile_question(update.effective_message, context, state)