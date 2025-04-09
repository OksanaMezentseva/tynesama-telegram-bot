import os
import asyncio
from telegram.ext import ApplicationBuilder
from handlers import register_handlers
from services.scheduler import send_daily_messages
from config import TELEGRAM_TOKEN

# This function will run once the bot is fully initialized
async def post_init(application):
    # Start the daily scheduled message task (doesn't block the bot)
    asyncio.create_task(send_daily_messages(application.bot))

# Render provides this environment variable automatically
RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

# Telegram will send updates to this path
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}{WEBHOOK_PATH}"

# Build the bot application with webhook support
app = (
    ApplicationBuilder()
    .token(TELEGRAM_TOKEN)       # Your Telegram bot token
    .post_init(post_init)        # Optional hook to run custom logic on startup
    .webhook_path(WEBHOOK_PATH)  # Set the webhook endpoint path
    .build()
)

# Register all command and message handlers
register_handlers(app)

# For debugging: log the webhook URL to Render logs
print(f"🌐 Bot running on webhook URL: {WEBHOOK_URL}")

# Start the webhook server on Render's provided port
app.run_webhook(
    listen="0.0.0.0",  # Listen on all network interfaces
    port=int(os.environ.get("PORT", 5000)),  # Get port from Render or default to 5000
    webhook_url=WEBHOOK_URL  # The full URL Telegram will use to send updates
)