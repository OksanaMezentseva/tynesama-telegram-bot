import asyncio
import datetime
from telegram import Bot
from services.utils import get_morning_message, get_evening_message
from services.subscription import load_subscribers


async def send_daily_messages(bot: Bot):
    # Run continuous loop to check and send daily messages at 08:00 and 21:00
    while True:
        now = datetime.datetime.now()
        next_morning = now.replace(hour=8, minute=0, second=0, microsecond=0)
        next_evening = now.replace(hour=21, minute=0, second=0, microsecond=0)

        if now >= next_morning:
            next_morning += datetime.timedelta(days=1)
        if now >= next_evening:
            next_evening += datetime.timedelta(days=1)

        sleep_until_morning = (next_morning - now).total_seconds()
        sleep_until_evening = (next_evening - now).total_seconds()

        await asyncio.sleep(min(sleep_until_morning, sleep_until_evening))

        current_time = datetime.datetime.now().time()
        subscribers = load_subscribers()

        if current_time.hour == 8:
            msg = get_morning_message()
        elif current_time.hour == 21:
            msg = get_evening_message()
        else:
            msg = None

        # Send message to all subscribed chat IDs
        if msg:
            for chat_id in subscribers:
                try:
                    await bot.send_message(chat_id=chat_id, text=msg)
                except Exception as e:
                    print(f"Failed to send to {chat_id}: {e}")

        await asyncio.sleep(60)  # Avoid sending multiple times per minute