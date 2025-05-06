import os
import asyncio
import logging
import time
from telegram.ext import ApplicationBuilder
from handlers import register_handlers
from services.scheduler import send_daily_messages
from services.db import init_db
from config import TELEGRAM_TOKEN

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(message)s",
    datefmt="%H:%M:%S"
)

# Called once when the bot starts
async def post_init(application):
    total_start = time.time()
    logging.info("🚀 post_init started")

    db_start = time.time()
    init_db()
    logging.info(f"⏱ init_db() completed in {time.time() - db_start:.2f}s")

    task_start = time.time()
    application.job_task = asyncio.create_task(send_daily_messages(application.bot))
    logging.info(f"🚀 Background task started in {time.time() - task_start:.2f}s")

    # render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
    # if not render_host:
    #     raise RuntimeError("RENDER_EXTERNAL_HOSTNAME is not set!")

    # webhook_url = f"https://{render_host}/webhook"
    # await application.bot.set_webhook(webhook_url)
    # logging.info(f"✅ Webhook manually set: {webhook_url}")

    logging.info(f"✅ post_init completed in {time.time() - total_start:.2f}s")

# Called once when the bot is shutting down
async def on_shutdown(application):
    task = getattr(application, "job_task", None)
    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            logging.info("🛑 Background task cancelled on shutdown")

# RENDER_EXTERNAL_HOSTNAME = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
# if not RENDER_EXTERNAL_HOSTNAME:
#     raise RuntimeError("RENDER_EXTERNAL_HOSTNAME is not set!")

# WEBHOOK_PATH = "/webhook"
# WEBHOOK_URL = f"https://{RENDER_EXTERNAL_HOSTNAME}{WEBHOOK_PATH}"

app = (
    ApplicationBuilder()
    .token(TELEGRAM_TOKEN)
    .post_init(post_init)
    .post_shutdown(on_shutdown)
    .build()
)

# Register command and message handlers
register_handlers(app)

logging.info("🤖 Bot is starting with polling...")
app.run_polling()
