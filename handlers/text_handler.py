from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services.utils import get_random_affirmation, get_random_breathing_tip
from services.subscription import is_subscribed
from handlers.command_handler import subscribe_command, unsubscribe_command
from services.user_state import UserStateManager
from services.db import save_feedback
import openai
import os
from services.button_labels import (
    BTN_TALK,
    BTN_BREATHING,
    BTN_AFFIRMATION,
    BTN_SUBSCRIBE,
    BTN_UNSUBSCRIBE,
    BTN_TOPICS,
    BTN_SOLIDS,
    BTN_BREASTFEEDING,
    BTN_SLEEP,
    BTN_PREGNANCY,
    BTN_BACK,
    BTN_FEEDBACK
)
from services.text_messages import (
    SYSTEM_PROMPT,
    SYSTEM_PROMPT_BREASTFEEDING,
    SYSTEM_PROMPT_SOLIDS,
    MSG_SUBSCRIBE_REQUIRED,
    MSG_READY_TO_LISTEN,
    MSG_CHOOSE_TOPIC,
    LOGIC_BACK_TO_MAIN_MENU,
    REPLY_BREASTFEEDING,
    REPLY_SOLIDS,
    REPLY_PREGNANCY,
    SYSTEM_PROMPT_PREGNANCY,
    REPLY_SLEEP,
    SYSTEM_PROMPT_SLEEP,
    MSG_FEEDBACK_THANKS,
    MSG_FEEDBACK_PROMPT
)

ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

openai.api_key = os.getenv("OPENAI_API_KEY")


async def choose_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [BTN_BREASTFEEDING, BTN_SOLIDS],
        [BTN_SLEEP, BTN_PREGNANCY],
        [BTN_BACK]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(MSG_CHOOSE_TOPIC, reply_markup=reply_markup)


async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    chat_id = update.effective_chat.id
    chat_id_str = str(chat_id)
    state = UserStateManager(chat_id_str)

    # Handle feedback message if waiting
    if state.get_step() == "waiting_for_feedback":
        save_feedback(chat_id_str, user_input)
        state.set_step("started")
        await update.message.reply_text(MSG_FEEDBACK_THANKS)
        if ADMIN_CHAT_ID:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"💬 Відгук від {chat_id_str}:\n{user_input}")
        return

    # SUBSCRIBE / UNSUBSCRIBE
    if user_input == BTN_SUBSCRIBE:
        await subscribe_command(update, context)
        return

    if user_input == BTN_UNSUBSCRIBE:
        await unsubscribe_command(update, context)
        return

    # FEEDBACK
    if user_input == BTN_FEEDBACK:
        state.set_step("waiting_for_feedback")
        await update.message.reply_text(MSG_FEEDBACK_PROMPT)
        return

    # AFFIRMATION / BREATHING
    if user_input == BTN_AFFIRMATION:
        affirmation = get_random_affirmation()
        await update.message.reply_text(affirmation)
        return

    if user_input == BTN_BREATHING:
        tip = get_random_breathing_tip()
        await update.message.reply_text(tip)
        return

    # TALK
    if user_input == BTN_TALK:
        if not is_subscribed(chat_id):
            await update.message.reply_text(MSG_SUBSCRIBE_REQUIRED)
            return
        state.set_step("waiting_for_gpt_question")
        await update.message.reply_text(MSG_READY_TO_LISTEN)
        return

    # TOPICS
    if user_input == BTN_TOPICS:
        state.set_step("choosing_topic")
        await choose_topic_handler(update, context)
        return

    if user_input == BTN_BACK:
        from handlers.command_handler import update_reply_keyboard
        state.set_step("started")
        state.set("topic", None)
        await update_reply_keyboard(update, context, message=LOGIC_BACK_TO_MAIN_MENU)
        return

    # TOPIC CHOICE
    if user_input == BTN_BREASTFEEDING:
        state.set("topic", "breastfeeding")
        await update.message.reply_text(REPLY_BREASTFEEDING)
        return

    if user_input == BTN_SOLIDS:
        state.set("topic", "solids")
        await update.message.reply_text(REPLY_SOLIDS)
        return

    if user_input == BTN_PREGNANCY:
        state.set("topic", "pregnancy")
        await update.message.reply_text(REPLY_PREGNANCY)
        return

    if user_input == BTN_SLEEP:
        state.set("topic", "sleep")
        await update.message.reply_text(REPLY_SLEEP)
        return

    # OTHER TEXT — GPT
    if not is_subscribed(chat_id):
        await update.message.reply_text(MSG_SUBSCRIBE_REQUIRED)
        return

    topic = state.get("topic")
    if topic == "breastfeeding":
        system_prompt = SYSTEM_PROMPT_BREASTFEEDING
    elif topic == "solids":
        system_prompt = SYSTEM_PROMPT_SOLIDS
    elif topic == "pregnancy":
        system_prompt = SYSTEM_PROMPT_PREGNANCY
    elif topic == "sleep":
        system_prompt = SYSTEM_PROMPT_SLEEP
    else:
        system_prompt = SYSTEM_PROMPT

    # Load GPT history by topic
    history = state.get_gpt_history(topic)
    messages = [{"role": "system", "content": system_prompt}]
    for pair in history[-3:]:
        messages.append({"role": "user", "content": pair["question"]})
        messages.append({"role": "assistant", "content": pair["reply"]})
    messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        bot_reply = response["choices"][0]["message"]["content"]
        state.add_gpt_interaction(user_input, bot_reply)
        await update.message.reply_text(bot_reply)

    except Exception as e:
        await update.message.reply_text("⚠️ Щось пішло не так. Спробуй ще раз пізніше.")
        print(f"GPT error for {chat_id}: {e}")