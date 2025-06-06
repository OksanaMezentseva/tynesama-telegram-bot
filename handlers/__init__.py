import logging
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from .command_handler import (
    start_command,
    subscribe_command,
    unsubscribe_command,
    test_db,
    support_command,
    handle_profile,
)
from .text_handler import handle_text_message, choose_topic_handler
from .voice_handler import handle_voice_message
from handlers.callback_handler import handle_profile_callback
from handlers.topic_choice import handle_topic_callback
from handlers.children_ages_choice import handle_children_ages_callback
from handlers.status_choice import handle_status_callback
from handlers.children_count_choice import handle_children_count_callback



# 🔽 Import all button labels
from services.button_labels import (
    BTN_TOPICS,
    BTN_PROFILE,
)

def register_handlers(app):
    logging.info("🔧 Registering command and message handlers...")

    # /start
    app.add_handler(CommandHandler("start", start_command))
    logging.debug("✅ Handler registered: /start")

    # /subscribe
    app.add_handler(CommandHandler("subscribe", subscribe_command))
    logging.debug("✅ Handler registered: /subscribe")

    # /unsubscribe
    app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
    logging.debug("✅ Handler registered: /unsubscribe")

    # /testdb (admin)
    app.add_handler(CommandHandler("testdb", test_db))
    logging.debug("✅ Handler registered: /testdb")

    # Topic selection (🧡 Обрати, що зараз хвилює)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{BTN_TOPICS}$"), choose_topic_handler))
    logging.debug("✅ Handler registered: choose_topic_handler")

    # Profile button (👩‍🍼 Мій профіль)
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(f"^{BTN_PROFILE}$"), handle_profile))
    logging.debug("✅ Handler registered: handle_profile")

    # Voice messages
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    logging.debug("✅ Handler registered: handle_voice_message")

    # All other text messages (GPT or feedback or flow)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    logging.debug("✅ Handler registered: handle_text_message")

    # Inline callback (e.g., edit profile)
    app.add_handler(CallbackQueryHandler(handle_profile_callback, pattern="^edit_profile$"))
    logging.debug("✅ Callback handler registered: edit_profile")

    app.add_handler(CallbackQueryHandler(handle_topic_callback, pattern=r"^(toggle_topic|save_topics)"))
    logging.debug("✅ Callback handler registered: topic_choice")

    # Inline callback: children ages selection
    app.add_handler(CallbackQueryHandler(handle_children_ages_callback, pattern=r"^(toggle_age|save_ages)"))
    logging.debug("✅ Callback handler registered: children_ages_choice")

    # Inline callback: status selection
    app.add_handler(CallbackQueryHandler(handle_status_callback, pattern=r"^status_choice:"))
    logging.debug("✅ Callback handler registered: status_choice")

    app.add_handler(CallbackQueryHandler(handle_children_count_callback, pattern=r"^children_count_choice:"))
    logging.debug("✅ Callback handler registered: children_count_choice")

    logging.info("✅ All handlers registered successfully.")