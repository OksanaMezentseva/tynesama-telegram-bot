import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton, Message, Update
from telegram.ext import ContextTypes

from db.session import SessionLocal
from repositories.profile_repository import ProfileRepository
from repositories.user_repository import UserRepository

from services.user_state import UserStateManager
from services.reply_utils import get_main_keyboard
from services.text_messages import MSG_MY_SPACE_MENU
from services.button_labels import (
    BTN_FEEDBACK, BTN_SUPPORT, BTN_SUBSCRIBE, BTN_UNSUBSCRIBE, BTN_BACK, BTN_PROFILE
)
from services.profile_constants import (
    CHILDREN_COUNT_1, CHILDREN_COUNT_2, CHILDREN_COUNT_3_PLUS
)

# Profile questions definition
PROFILE_QUESTIONS = [
    {
        "key": "status",
        "question": "Обери, яка в тебе ситуація зараз 💛",
        "type": "inline_choice",
        "options": []
    },
    {
        "key": "children_count",
        "question": "Скільки у тебе діток?",
        "type": "inline_choice",
        "options": []
    },
    {
        "key": "children_ages",
        "question": (
            "У якому віковому періоді зараз твої дітки? "
            "Можна обрати кілька варіантів, якщо діти різного віку 💛"
        ),
        "type": "multi_choice",
        "options": [
            "0–6 міс", "7–12 міс", "1–3 роки",
            "4–7 років", "8+ років"
        ]
    },
    {
        "key": "preferred_topics",
        "question": "Які теми тобі цікаві? Можна обрати кілька:",
        "type": "multi_choice",
        "options": [
            "🤱 Грудне вигодовування", "🥣 Прикорм", "👼 Сон малюка",
            "🤰 Вагітність", "🧠 Розвиток дитини", "😡 Істерики, емоції",
            "💛 Емоції мами", "💬 Підтримка з боку партнера",
            "⏰ Денний режим", "🦷 Прорізування зубів"
        ]
    }
]


async def send_next_profile_question(message: Message, context: ContextTypes.DEFAULT_TYPE, state: UserStateManager):
    """
    Sends the next unanswered profile question.
    If all questions are answered, saves profile and shows success message.
    """
    chat_id = message.chat.id
    index = state.get("profile_progress", 0)
    profile_data = state.get("profile_data", {})

    while index < len(PROFILE_QUESTIONS):
        question = PROFILE_QUESTIONS[index]
        key = question["key"]

        # Set current step and progress
        state.set_step(f"profile_q{index}")
        state.set("profile_progress", index)

        if key == "status":
            from handlers.status_choice import send_status_keyboard
            await send_status_keyboard(chat_id, context, state)
            return

        if key == "children_count":
            from handlers.children_count_choice import send_children_count_keyboard
            await send_children_count_keyboard(chat_id, context, state)
            return

        if key == "children_ages":
            from handlers.children_ages_choice import send_children_ages_keyboard
            await send_children_ages_keyboard(chat_id, context, state)
            return

        if key == "preferred_topics":
            from handlers.topic_choice import send_topic_selection_keyboard
            await send_topic_selection_keyboard(chat_id, context, state)
            return

        # ReplyKeyboard fallback
        if question["type"] == "choice":
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(opt)] for opt in question["options"]],
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Обери відповідь 👇"
            )
            await context.bot.send_message(chat_id=chat_id, text=question["question"], reply_markup=keyboard)
            return

        await context.bot.send_message(chat_id=chat_id, text=question["question"])
        return

    # ✅ All questions answered — save profile
    state.set("profile", profile_data)
    state.set("profile_completed", True)
    state.set_step("started")

    # Save profile to database using repository
    session = SessionLocal()
    try:
        profile_repo = ProfileRepository(session)
        profile_repo.save(str(chat_id), profile_data)
        session.commit()
        logging.info(f"✅ Profile completed and saved for {chat_id}")
    except Exception as e:
        session.rollback()
        logging.warning(f"❌ Failed to save profile for {chat_id}: {e}")
    finally:
        session.close()

    # Return to previous menu
    previous_menu = state.get("previous_menu")

    if previous_menu == "my_space":
        session = SessionLocal()
        try:
            user_repo = UserRepository(session)
            user = user_repo.get_by_telegram_id(str(chat_id))
            subscribed = user.is_subscribed if user else False
        finally:
            session.close()

        space_keyboard = [
            [BTN_FEEDBACK, BTN_SUPPORT],
            [BTN_PROFILE, BTN_UNSUBSCRIBE if subscribed else BTN_SUBSCRIBE],
            [BTN_BACK]
        ]
        reply_markup = ReplyKeyboardMarkup(space_keyboard, resize_keyboard=True)
        state.set_step("my_space")
        await context.bot.send_message(chat_id=chat_id, text="✅ Твій профіль збережено 💛", reply_markup=reply_markup)
    else:
        await context.bot.send_message(
            chat_id=chat_id,
            text="✅ Твій профіль збережено 💛",
            reply_markup=get_main_keyboard()
        )


async def handle_profile_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles user text answer for choice-type questions (not inline).
    """
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

    # Skip inline types from here
    if expected_type not in {"choice"}:
        return

    # Validate keyboard answer
    valid_options = [opt.lower() for opt in question["options"]]
    if user_input.lower() not in valid_options:
        await update.message.reply_text("Будь ласка, обери один із варіантів з клавіатури 🙏")
        await send_next_profile_question(update.message, context, state)
        return

    # Save answer to state
    profile_data[key] = user_input
    state.set("profile_data", profile_data)
    state.set("profile_progress", current_index + 1)

    await send_next_profile_question(update.message, context, state)