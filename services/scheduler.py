import asyncio
import datetime
import logging
from telegram import Bot
from zoneinfo import ZoneInfo

from services.utils import get_morning_message, get_evening_message
from db.session import SessionLocal
from repositories.user_repository import UserRepository

# Set timezone to Kyiv
KYIV_TZ = ZoneInfo("Europe/Kyiv")


async def send_daily_messages(bot: Bot):
    """
    Background task that continuously sends scheduled messages to subscribed users
    at 08:00 and 21:00 Kyiv time.
    """
    logging.info("🕒 Scheduler started...")

    try:
        while True:
            now = datetime.datetime.now(KYIV_TZ)
            today = now.date()

            # Determine next scheduled times for morning and evening
            next_morning = datetime.datetime.combine(today, datetime.time(8, 0), tzinfo=KYIV_TZ)
            next_evening = datetime.datetime.combine(today, datetime.time(21, 0), tzinfo=KYIV_TZ)

            if now >= next_morning:
                next_morning += datetime.timedelta(days=1)
            if now >= next_evening:
                next_evening += datetime.timedelta(days=1)

            # Find the nearest scheduled time
            next_send_time = min(next_morning, next_evening)
            wait_seconds = (next_send_time - now).total_seconds()

            logging.info(f"📆 Next message scheduled at {next_send_time.strftime('%Y-%m-%d %H:%M:%S')}")

            # Sleep until the next scheduled time
            await asyncio.sleep(wait_seconds)

            # Choose the appropriate message
            current_hour = next_send_time.hour
            msg = get_morning_message() if current_hour == 8 else get_evening_message()

            if not msg:
                logging.warning("⚠️ No message generated, skipping broadcast.")
                continue

            # Retrieve subscribed users from the database
            try:
                session = SessionLocal()
                try:
                    repo = UserRepository(session)
                    subscribers = repo.get_all_subscribed_users()
                finally:
                    session.close()
            except Exception as e:
                logging.error(f"❌ Error retrieving subscribers: {e}")
                subscribers = []

            # Send the message to each subscribed user
            for user in subscribers:
                try:
                    await bot.send_message(chat_id=int(user.telegram_id), text=msg)
                except Exception as e:
                    logging.warning(f"❌ Failed to send message to {user.telegram_id}: {e}")

            # Safety pause to prevent duplicate sends if something goes wrong
            await asyncio.sleep(60)

    except asyncio.CancelledError:
        logging.info("🛑 send_daily_messages task was cancelled cleanly")
        raise