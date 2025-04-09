import asyncio
import datetime
from telegram import Bot
from services.utils import get_morning_message, get_evening_message
from services.db import get_all_subscribed_users

async def send_daily_messages(bot: Bot):
    """Continuously sends messages at 08:00 and 21:00 to subscribed users."""
    print("Scheduler started...")

    while True:
        now = datetime.datetime.now()
        today = now.date()

        next_morning = datetime.datetime.combine(today, datetime.time(8, 0))
        next_evening = datetime.datetime.combine(today, datetime.time(21, 0))

        if now >= next_morning:
            next_morning += datetime.timedelta(days=1)
        if now >= next_evening:
            next_evening += datetime.timedelta(days=1)

        # Determine what will happen next — morning or evening
        next_send_time = min(next_morning, next_evening)
        wait_seconds = (next_send_time - now).total_seconds()

        print(f"Next message scheduled at {next_send_time.strftime('%Y-%m-%d %H:%M:%S')}")

        await asyncio.sleep(wait_seconds)

        # what type of message to send
        current_hour = next_send_time.hour
        msg = None
        if current_hour == 8:
            msg = get_morning_message()
        elif current_hour == 21:
            msg = get_evening_message()

        if msg:
            subscribers = get_all_subscribed_users()
            for user in subscribers:
                try:
                    await bot.send_message(chat_id=int(user.telegram_id), text=msg)
                except Exception as e:
                    print(f"❌ Failed to send to {user.telegram_id}: {e}")

        await asyncio.sleep(60)  # Safety pause to avoid rapid re-sending
