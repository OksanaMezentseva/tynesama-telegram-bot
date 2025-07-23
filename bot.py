import os
import asyncio
import logging
import time
from telegram.ext import ApplicationBuilder
from handlers import register_handlers
from services.scheduler import send_daily_messages
from db.session import init_db  # ⬅️ changed import to new OOP-based init
from config import TELEGRAM_TOKEN

# Configure logging format and level
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

# Called once after the bot is initialized
async def post_init(application):
    total_start = time.time()
    logging.info("🚀 post_init started")

    # Initialize the database (tables, engine)
    db_start = time.time()
    init_db()
    logging.info(f"⏱ init_db() completed in {time.time() - db_start:.2f}s")

    # Start the background task for sending daily messages
    task_start = time.time()
    application.job_task = asyncio.create_task(send_daily_messages(application.bot))
    logging.info(f"🚀 Background task started in {time.time() - task_start:.2f}s")

    # Optional: webhook setup (disabled for now)
    # render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    # if not render_host:
    #     raise RuntimeError("RENDER_EXTERNAL_HOSTNAME is not set!")
    # webhook_url = f"https://{render_host}/webhook"
    # await application.bot.set_webhook(webhook_url)
    # logging.info(f"✅ Webhook manually set: {webhook_url}")

    logging.info(f"✅ post_init completed in {time.time() - total_start:.2f}s")

# Called once when the bot shuts down
async def on_shutdown(application):
    task = getattr(application, "job_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logging.info("🛑 Background task cancelled on shutdown")

# Create the application instance
app = (
    ApplicationBuilder()
    .token(TELEGRAM_TOKEN)
    .post_init(post_init)
    .post_shutdown(on_shutdown)
    .build()
)

# Register command and message handlers
register_handlers(app)

# Start polling loop
logging.info("🤖 Bot is starting with polling...")
app.run_polling()