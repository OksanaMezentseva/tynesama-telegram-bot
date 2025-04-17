import asyncio
import datetime
import logging
from telegram import Bot

async def send_daily_messages(bot: Bot):
    """Continuously sends messages at 08:00 and 21:00 to subscribed users."""
    logging.info("🕒 Scheduler started...")

    try:
        while True:
            now = datetime.datetime.now()
            today = now.date()

            next_morning = datetime.datetime.combine(today, datetime.time(8, 0))
            next_evening = datetime.datetime.combine(today, datetime.time(21, 0))

            if now >= next_morning:
                next_morning += datetime.timedelta(days=1)
            if now >= next_evening:
                next_evening += datetime.timedelta(days=1)

            next_send_time = min(next_morning, next_evening)
            wait_seconds = (next_send_time - now).total_seconds()

            logging.info(f"📆 Next message scheduled at {next_send_time.strftime('%Y-%m-%d %H:%M:%S')}")

            await asyncio.sleep(wait_seconds)

            from services.utils import get_morning_message, get_evening_message
            from services.db import get_all_subscribed_users

            current_hour = next_send_time.hour
            msg = get_morning_message() if current_hour == 8 else get_evening_message()

            if not msg:
                logging.warning("⚠️ No message generated, skipping broadcast.")
                continue

            try:
                subscribers = get_all_subscribed_users()
                for user in subscribers:
                    try:
                        await bot.send_message(chat_id=int(user.telegram_id), text=msg)
                    except Exception as e:
                        logging.warning(f"❌ Failed to send message to {user.telegram_id}: {e}")
            except Exception as e:
                logging.error(f"❌ Error retrieving or sending messages: {e}")

            await asyncio.sleep(60)  # Safety pause to avoid duplicate sends

    except asyncio.CancelledError:
        logging.info("🛑 send_daily_messages task was cancelled cleanly")
        # Re-raise so the task exits properly
        raise