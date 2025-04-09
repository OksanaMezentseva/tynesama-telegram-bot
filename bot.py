import asyncio
from telegram.ext import ApplicationBuilder
from handlers import register_handlers
from services.scheduler import send_daily_messages
from config import TELEGRAM_TOKEN

async def post_init(application):
    # Launch scheduler after bot is ready
    asyncio.create_task(send_daily_messages(application.bot))

app = ApplicationBuilder().token(TELEGRAM_TOKEN).post_init(post_init).build()
register_handlers(app)

print("Bot is running...")
app.run_polling()