from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from services.user_state import UserStateManager
from services.db import save_profile
from handlers.command_handler import update_reply_keyboard
from services.profile_constants import (
    STATUS_PREGNANT, STATUS_HAS_CHILDREN, STATUS_BOTH, STATUS_NONE,
    CHILDREN_COUNT_1, CHILDREN_COUNT_2, CHILDREN_COUNT_3_PLUS,
    BREASTFEEDING_YES, BREASTFEEDING_NO, BREASTFEEDING_PLAN, BREASTFEEDING_DONE,
    COUNTRY_UA, COUNTRY_ABROAD
)

# Centralized profile questions using constants
PROFILE_QUESTIONS = [
    {
        "key": "status",
        "question": "Чи ти зараз вагітна або маєш діток?",
        "type": "choice",
        "options": [STATUS_PREGNANT, STATUS_HAS_CHILDREN, STATUS_BOTH, STATUS_NONE]
    },
    {
        "key": "children_count",
        "question": "Скільки у тебе діток?",
        "type": "choice",
        "options": [CHILDREN_COUNT_1, CHILDREN_COUNT_2, CHILDREN_COUNT_3_PLUS]
    },
    {
        "key": "children_ages",
        "question": "Скільки років або місяців кожній дитині? Напиши через кому.",
        "type": "text"
    },
    {
        "key": "breastfeeding",
        "question": "Чи ти зараз годуєш грудьми?",
        "type": "choice",
        "options": [BREASTFEEDING_YES, BREASTFEEDING_NO, BREASTFEEDING_PLAN, BREASTFEEDING_DONE]
    },
    {
        "key": "country",
        "question": "Ти зараз живеш в Україні чи за кордоном?",
        "type": "choice",
        "options": [COUNTRY_UA, COUNTRY_ABROAD]
    }
]

# Show next question based on progress + conditional logic
async def send_next_profile_question(update: Update, context: ContextTypes.DEFAULT_TYPE, state: UserStateManager):
    index = state.get("profile_progress", 0)
    profile_data = state.get("profile_data", {})

    while index < len(PROFILE_QUESTIONS):
        question = PROFILE_QUESTIONS[index]
        key = question["key"]
        status = profile_data.get("status")

        # Skip based on logic from status
        if status == STATUS_PREGNANT and key in {"children_count", "children_ages", "breastfeeding"}:
            index += 1
            continue
        if status == STATUS_NONE and key in {"children_count", "children_ages", "breastfeeding"}:
            index += 1
            continue

        state.set_step(f"profile_q{index}")
        state.set("profile_progress", index)

        if question["type"] == "choice":
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(opt)] for opt in question["options"]],
                resize_keyboard=True,
                one_time_keyboard=True
            )
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=question["question"],
                reply_markup=keyboard
            )
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=question["question"]
            )

        return

    # End of profile flow
    state.set("profile", profile_data)
    state.set_step("started")
    save_profile(str(update.effective_chat.id), profile_data)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="✅ Дякую! Твій профіль збережено 💛"
    )
    await update_reply_keyboard(update, context, message="📋 Ти повернулась до головного меню")

# Handle answer and continue
async def handle_profile_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    chat_id = str(update.effective_chat.id)
    state = UserStateManager(chat_id)

    profile_data = state.get("profile_data", {})
    current_index = state.get("profile_progress", 0)

    if current_index >= len(PROFILE_QUESTIONS):
        await update.message.reply_text("Невідомий крок 🤔")
        return

    question = PROFILE_QUESTIONS[current_index]
    key = question["key"]
    expected_type = question["type"]

    if expected_type == "choice":
        valid_options = [opt.lower() for opt in question["options"]]
        if user_input.lower() not in valid_options:
            await update.message.reply_text("Будь ласка, обери один із варіантів з клавіатури 🙏")
            await send_next_profile_question(update, context, state)
            return

    profile_data[key] = user_input
    state.set("profile_data", profile_data)
    current_index += 1
    state.set("profile_progress", current_index)

    await send_next_profile_question(update, context, state)