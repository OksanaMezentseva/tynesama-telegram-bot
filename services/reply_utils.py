from telegram import Update, Message, ReplyKeyboardMarkup
from services.button_labels import BTN_TALK, BTN_TOPICS, BTN_PAUSE, BTN_SPACE

def get_main_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        [
            [BTN_SPACE, BTN_TALK],
            [BTN_TOPICS, BTN_PAUSE]
        ],
        resize_keyboard=True
    )

async def update_reply_keyboard(update_or_message, context, message: str):
    """
    Sends the main menu keyboard with a message.
    Accepts either Update or Message object.
    """
    keyboard = get_main_keyboard()

    if isinstance(update_or_message, Update):
        await update_or_message.message.reply_text(message, reply_markup=keyboard)
    elif isinstance(update_or_message, Message):
        await context.bot.send_message(
            chat_id=update_or_message.chat.id,
            text=message,
            reply_markup=keyboard
        )
    else:
        raise TypeError("update_reply_keyboard: expected Update or Message")