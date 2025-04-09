import os
import asyncio
from datetime import datetime
from telegram.ext import ApplicationBuilder
from handlers import register_handlers
from services.scheduler import send_daily_messages
from config import TELEGRAM_TOKEN

# Simple logger with timestamp
def log(message: str):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

# This function will run once the bot is fully initialized
async def post_init(application):
    # Launch background task
    asyncio.create_task(send_daily_messages(application.bot))

    # Check if hostname is defined
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    if not render_host:
        raise RuntimeError("RENDER_EXTERNAL_HOSTNAME is not set!")

    webhook_url = f"https://{render_host}/webhook"

    # Manually set webhook for Telegram
    await application.bot.set_webhook(webhook_url, timeout=10)
    log(f"✅ Webhook manually set: {webhook_url}")

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
    .token(TELEGRAM_TOKEN)       # Your Telegram bot token
    .post_init(post_init)        # Custom logic after startup
    .webhook_path(WEBHOOK_PATH)  # Set the webhook endpoint path
    .build()
)

# Register all command and message handlers
register_handlers(app)

log(f"🌐 Bot running on webhook URL: {WEBHOOK_URL}")

# Start the webhook server on Render's provided port
app.run_webhook(
    listen="0.0.0.0",  # Listen on all network interfaces
    port=int(os.environ.get("PORT", 5000)),  # Use Render's assigned port
    webhook_url=WEBHOOK_URL  # Full webhook URL for Telegram
)