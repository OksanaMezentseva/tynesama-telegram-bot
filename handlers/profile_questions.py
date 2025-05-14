import logging
from telegram import ReplyKeyboardMarkup, KeyboardButton, Message, Update
from telegram.ext import ContextTypes
from services.user_state import UserStateManager
from services.reply_utils import get_main_keyboard
from services.db import save_profile
from services.subscription import is_subscribed
from services.text_messages import MSG_MY_SPACE_MENU
from services.button_labels import (
    BTN_FEEDBACK, BTN_SUPPORT, BTN_SUBSCRIBE, BTN_UNSUBSCRIBE, BTN_BACK, BTN_PROFILE
)
from services.profile_constants import (
    STATUS_PREGNANT, STATUS_HAS_CHILDREN, STATUS_BOTH, STATUS_NONE,
    BREASTFEEDING_YES, BREASTFEEDING_NO, BREASTFEEDING_PLAN, BREASTFEEDING_DONE,
    COUNTRY_UA, COUNTRY_ABROAD,
    CHILDREN_COUNT_1, CHILDREN_COUNT_2, CHILDREN_COUNT_3_PLUS
)

# Profile questionnaire configuration
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


async def send_next_profile_question(message: Message, context: ContextTypes.DEFAULT_TYPE, state: UserStateManager):
    """
    Sends the next unanswered profile question.
    On completion, saves the profile and returns to previous menu.
    """
    chat_id = message.chat.id
    index = state.get("profile_progress", 0)
    profile_data = state.get("profile_data", {})

    # Loop through profile questions
    while index < len(PROFILE_QUESTIONS):
        question = PROFILE_QUESTIONS[index]
        key = question["key"]
        status = profile_data.get("status")

        # Skip questions based on user's status
        if status in {STATUS_PREGNANT, STATUS_NONE} and key in {"children_count", "children_ages", "breastfeeding"}:
            index += 1
            continue

        # Set current step and progress
        state.set_step(f"profile_q{index}")
        state.set("profile_progress", index)

        # Send question
        if question["type"] == "choice":
            keyboard = ReplyKeyboardMarkup(
                [[KeyboardButton(opt)] for opt in question["options"]],
                resize_keyboard=True,
                one_time_keyboard=True,
                input_field_placeholder="Обери відповідь 👇"
            )
            await context.bot.send_message(chat_id=chat_id, text=question["question"], reply_markup=keyboard)
        else:
            await context.bot.send_message(chat_id=chat_id, text=question["question"])

        return  # Wait for answer

    # Profile complete
    state.set("profile", profile_data)
    state.set("profile_completed", True)
    state.set_step("started")
    save_profile(str(chat_id), profile_data)
    logging.info(f"✅ Profile completed and saved for {chat_id}")

    previous_menu = state.get("previous_menu")

    if previous_menu == "my_space":
        subscribed = is_subscribed(str(chat_id))
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
    Handles user's answer and moves to the next question or ends the flow.
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

    # Validate choice-type answers
    if expected_type == "choice":
        valid_options = [opt.lower() for opt in question["options"]]
        if user_input.lower() not in valid_options:
            await update.message.reply_text("Будь ласка, обери один із варіантів з клавіатури 🙏")
            await send_next_profile_question(update.message, context, state)
            return

    # Save answer and proceed
    profile_data[key] = user_input
    state.set("profile_data", profile_data)
    state.set("profile_progress", current_index + 1)

    await send_next_profile_question(update.message, context, state)
