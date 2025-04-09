from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from services.utils import get_random_affirmation, get_random_breathing_tip
from services.subscription import is_subscribed
from handlers.command_handler import subscribe_command, unsubscribe_command
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
    BTN_BACK
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
    SYSTEM_PROMPT_SLEEP
)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# choose_topic_handler
async def choose_topic_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle '🧡 Обрати, що зараз хвилює' button click."""
    keyboard = [
        [BTN_BREASTFEEDING, BTN_SOLIDS],
        [BTN_SLEEP, BTN_PREGNANCY],
        [BTN_BACK]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        MSG_CHOOSE_TOPIC,
        reply_markup=reply_markup
    )

# handle_text_message
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text.strip()
    chat_id = update.effective_chat.id

    # Handle subscription toggle buttons
    if user_input == BTN_SUBSCRIBE:
        await subscribe_command(update, context)
        return

    if user_input == BTN_UNSUBSCRIBE:
        await unsubscribe_command(update, context)
        return

    # Handle predefined buttons
    if user_input == BTN_AFFIRMATION:
        affirmation = get_random_affirmation()
        await update.message.reply_text(affirmation)
        return

    if user_input == BTN_BREATHING:
        tip = get_random_breathing_tip()
        await update.message.reply_text(tip)
        return

    if user_input == BTN_TALK:
        if not is_subscribed(chat_id):
            await update.message.reply_text(MSG_SUBSCRIBE_REQUIRED)
            return
        await update.message.reply_text(MSG_READY_TO_LISTEN)
        return

    if user_input == BTN_TOPICS:
        await choose_topic_handler(update, context)
        return

    if user_input == BTN_BACK:
        from handlers.command_handler import update_reply_keyboard
        await update_reply_keyboard(update, context, message=LOGIC_BACK_TO_MAIN_MENU)
        return

    if user_input == BTN_BREASTFEEDING:
        context.user_data["topic"] = "breastfeeding"
        await update.message.reply_text(REPLY_BREASTFEEDING)
        return

    if user_input == BTN_SOLIDS:
        context.user_data["topic"] = "solids"
        await update.message.reply_text(REPLY_SOLIDS)
        return
    
    if user_input == BTN_PREGNANCY:
        context.user_data["topic"] = "pregnancy"
        await update.message.reply_text(REPLY_PREGNANCY)
        return
    
    if user_input == BTN_SLEEP:
        context.user_data["topic"] = "sleep"
        from services.text_messages import REPLY_SLEEP
        await update.message.reply_text(REPLY_SLEEP)
        return


    # Handle custom user message via OpenAI (only for subscribers)
    if not is_subscribed(chat_id):
        await update.message.reply_text(MSG_SUBSCRIBE_REQUIRED)
        return

    # Select system prompt based on active topic
    topic = context.user_data.get("topic")
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


    system_message = {"role": "system", "content": system_prompt}
    user_message = {"role": "user", "content": user_input}
    messages = [system_message, user_message]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )

    bot_reply = response["choices"][0]["message"]["content"]
    await update.message.reply_text(bot_reply)