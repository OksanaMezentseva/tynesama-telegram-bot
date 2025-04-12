import os
import asyncio
import logging
from telegram.ext import ApplicationBuilder
from handlers import register_handlers
from services.scheduler import send_daily_messages
from config import TELEGRAM_TOKEN
from services.db import init_db


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

# This function will run once the bot is fully initialized
async def post_init(application):

    # Initialize the database
    init_db()
    
    # Launch background task
    asyncio.create_task(send_daily_messages(application.bot))

    # Check if hostname is defined
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not render_host:
        raise RuntimeError("RENDER_EXTERNAL_HOSTNAME is not set!")

    webhook_url = f"https://{render_host}/webhook"

    # Manually set webhook for Telegram
    await application.bot.set_webhook(webhook_url)
    logging.info(f"✅ Webhook manually set: {webhook_url}")

# Render provides this environment variable automatically
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if not RENDER_EXTERNAL_HOSTNAME:
    raise RuntimeError("RENDER_EXTERNAL_HOSTNAME is not set!")

# Telegram will send updates to this path
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}{WEBHOOK_PATH}"

# Build the bot application with webhook support
app = (
    ApplicationBuilder()
    .token(TELEGRAM_TOKEN)
    .post_init(post_init)
    .build()
)

# Register all command and message handlers
register_handlers(app)

logging.info(f"🌐 Bot running on webhook URL: {WEBHOOK_URL}")

# Start the webhook server on Render's provided port
app.run_webhook(
    listen="0.0.0.0",
    port=int(os.environ.get("PORT", 5000)),
    webhook_url=WEBHOOK_URL,
    url_path=WEBHOOK_PATH
)