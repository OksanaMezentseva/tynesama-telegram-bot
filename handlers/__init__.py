from .command_handler import start_command, subscribe_command, unsubscribe_command, test_db
from .text_handler import handle_text_message, choose_topic_handler
from .voice_handler import handle_voice_message
from telegram.ext import CommandHandler, MessageHandler, filters


def register_handlers(app):
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("🧡 Обрати, що зараз хвилює"), choose_topic_handler)
    )
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    app.add_handler(CommandHandler("testdb", test_db))
