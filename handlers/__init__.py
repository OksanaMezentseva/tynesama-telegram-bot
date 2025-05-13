import logging
from .command_handler import start_command, subscribe_command, unsubscribe_command, test_db, support_command
from .text_handler import handle_text_message, choose_topic_handler
from handlers.callback_handler import handle_profile_callback
from .voice_handler import handle_voice_message
from telegram.ext import CommandHandler, MessageHandler, filters, CallbackQueryHandler
from services.button_labels import BTN_SUPPORT


def register_handlers(app):
    logging.info("🔧 Registering command and message handlers...")

    app.add_handler(CommandHandler("start", start_command))
    logging.debug("✅ Handler registered: /start")

    app.add_handler(CommandHandler("subscribe", subscribe_command))
    logging.debug("✅ Handler registered: /subscribe")

    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    logging.debug("✅ Handler registered: /unsubscribe")

    app.add_handler(
        MessageHandler(filters.TEXT & filters.Regex("🧡 Обрати, що зараз хвилює"), choose_topic_handler)
    )
    logging.debug("✅ Handler registered: choose_topic_handler")

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    logging.debug("✅ Handler registered: handle_text_message")

    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    logging.debug("✅ Handler registered: handle_voice_message")

    app.add_handler(CommandHandler("testdb", test_db))
    logging.debug("✅ Handler registered: /testdb")

    app.add_handler(CallbackQueryHandler(handle_profile_callback, pattern="^edit_profile$"))
    logging.debug("✅ Callback handler registered: edit_profile")

    logging.info("✅ All handlers registered successfully.")
