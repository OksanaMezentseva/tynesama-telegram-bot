import logging
import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from services.utils import (
    get_random_affirmation,
    get_random_breathing_tip,
    is_prompt_injection,
    contains_pii,
    send_support_buttons
)
from services.subscription import is_subscribed
from services.user_state import UserStateManager
from services.db import save_feedback
from services.reply_utils import update_reply_keyboard  # ✅ Correct import to avoid circular dependency
from handlers.command_handler import subscribe_command, unsubscribe_command
from services.gpt_utils import ask_gpt_with_history
from services.button_labels import (
    BTN_TALK, BTN_BREATHING, BTN_AFFIRMATION, BTN_SUBSCRIBE, BTN_UNSUBSCRIBE,
    BTN_TOPICS, BTN_SOLIDS, BTN_BREASTFEEDING, BTN_SLEEP, BTN_PREGNANCY, BTN_BACK,
    BTN_FEEDBACK, BTN_SUPPORT, BTN_PAUSE, BTN_SPACE, BTN_PROFILE
)
from services.text_messages import (
    MSG_SUBSCRIBE_REQUIRED, MSG_READY_TO_LISTEN, MSG_CHOOSE_TOPIC,
    LOGIC_BACK_TO_MAIN_MENU, REPLY_BREASTFEEDING, REPLY_SOLIDS,
    REPLY_PREGNANCY, REPLY_SLEEP, MSG_FEEDBACK_THANKS, MSG_FEEDBACK_PROMPT,
    MSG_PAUSE_MENU, MSG_MY_SPACE_MENU
)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")


async def choose_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Shows the topic selection keyboard.
    """
    keyboard = [
        [BTN_BREASTFEEDING, BTN_SOLIDS],
        [BTN_SLEEP, BTN_PREGNANCY],
        [BTN_BACK]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(MSG_CHOOSE_TOPIC, reply_markup=reply_markup)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handles all incoming text messages from the user.
    Includes state transitions, GPT-based replies, feedback, subscriptions, and safety checks.
    """
    user_input = update.message.text.strip()
    chat_id = update.effective_chat.id
    chat_id_str = str(chat_id)
    state = UserStateManager(chat_id_str)

    # 🛡️ Prompt injection check
    if is_prompt_injection(user_input):
        await update.message.reply_text("З міркувань безпеки я не можу відповісти на цей запит 🙈")
        return

    # 🔒 PII filtering
    if contains_pii(user_input):
        await update.message.reply_text(
            "Будь ласка, не вводь особисті дані (телефон, адреса, email) 🙏 "
            "Я тут, щоб підтримати тебе — але твоя приватність понад усе 💛"
        )
        return

    # 💬 Feedback flow
    if state.get_step() == "waiting_for_feedback":
        save_feedback(chat_id_str, user_input)
        state.set_step("started")
        await update.message.reply_text(MSG_FEEDBACK_THANKS)
        if ADMIN_CHAT_ID:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"\U0001F4AC Відгук від {chat_id_str}:\n{user_input}")
        return

    # 📥 Subscription handling
    if user_input == BTN_SUBSCRIBE:
        await subscribe_command(update, context)
        return

    if user_input == BTN_UNSUBSCRIBE:
        await unsubscribe_command(update, context)
        return

    # 💌 Ask for feedback
    if user_input == BTN_FEEDBACK:
        state.set_step("waiting_for_feedback")
        await update.message.reply_text(MSG_FEEDBACK_PROMPT)
        return

    # 🌸 Affirmation
    if user_input == BTN_AFFIRMATION:
        await update.message.reply_text(get_random_affirmation())
        return

    # 🧘 Breathing tip
    if user_input == BTN_BREATHING:
        await update.message.reply_text(get_random_breathing_tip())
        return

    # 💬 Free-form GPT chat
    if user_input == BTN_TALK:
        state.set_step("waiting_for_gpt_question")
        await update.message.reply_text(MSG_READY_TO_LISTEN)
        return

    # 🧡 Choose a topic
    if user_input == BTN_TOPICS:
        state.set_step("choosing_topic")
        await choose_topic_handler(update, context)
        return

    # ⏸ Pause menu
    if user_input == BTN_PAUSE:
        pause_keyboard = ReplyKeyboardMarkup(
            [
                [BTN_AFFIRMATION],
                [BTN_BREATHING],
                [BTN_BACK]
            ],
            resize_keyboard=True
        )
        state.set_step("pause_menu")
        await update.message.reply_text(MSG_PAUSE_MENU, reply_markup=pause_keyboard)
        return

    # 👩‍🍼 My Space (user settings and support)
    if user_input == BTN_SPACE:
        subscribed = is_subscribed(chat_id)

        space_keyboard = [
            [BTN_PROFILE, BTN_SUPPORT],
            [BTN_SUBSCRIBE if not subscribed else BTN_UNSUBSCRIBE, BTN_FEEDBACK],
            [BTN_BACK]
        ]

        reply_markup = ReplyKeyboardMarkup(space_keyboard, resize_keyboard=True)
        state.set_step("my_space")
        await update.message.reply_text(MSG_MY_SPACE_MENU, reply_markup=reply_markup)
        return

    # 📋 Profile questionnaire handling
    if state.get_step().startswith("profile_q"):
        from handlers.profile_questions import handle_profile_answer
        await handle_profile_answer(update, context)
        return

    # 🔙 Back button logic
    if user_input == BTN_BACK:
        step = state.get_step()

        if step in {"choosing_topic", "pause_menu", "my_space"}:
            state.set_step("started")
            state.set("topic", None)
            await update_reply_keyboard(update, context, message=LOGIC_BACK_TO_MAIN_MENU)
            return

        # Default fallback to main menu
        state.set_step("started")
        await update_reply_keyboard(update, context, message=LOGIC_BACK_TO_MAIN_MENU)
        return

    # 🛟 Support options
    if user_input == BTN_SUPPORT:
        await send_support_buttons(update, context)
        return

    # 🍼 Topic-based reply
    topics_map = {
        BTN_BREASTFEEDING: ("breastfeeding", REPLY_BREASTFEEDING),
        BTN_SOLIDS: ("solids", REPLY_SOLIDS),
        BTN_PREGNANCY: ("pregnancy", REPLY_PREGNANCY),
        BTN_SLEEP: ("sleep", REPLY_SLEEP)
    }

    if user_input in topics_map:
        topic_key, reply = topics_map[user_input]
        state.set("topic", topic_key)
        await update.message.reply_text(reply)
        return

    # 🧠 GPT fallback
    try:
        bot_reply = await ask_gpt_with_history(state, user_input)
        await update.message.reply_text(bot_reply)
    except Exception as e:
        await update.message.reply_text("\u26a0\ufe0f Щось пішло не так. Спробуй ще раз пізніше.")
        logging.warning(f"\u26a0\ufe0f GPT error for {chat_id_str}: {e}")
