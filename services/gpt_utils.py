import openai
import logging
from openai.error import Timeout


def ask_gpt_with_history(messages: list, timeout: int = 10) -> str:
    """
    Sends a list of messages to GPT and returns the reply.
    Handles timeout and general errors gracefully.
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            timeout=timeout  # Set timeout to avoid long waits
        )
        return response["choices"][0]["message"]["content"]

    except Timeout:
        logging.warning("⏱ GPT request timed out.")
        return "GPT відповідає повільно. Спробуй ще раз трохи пізніше ⏳"

    except Exception as e:
        logging.error(f"❌ GPT general error: {e}")
        return "⚠️ Щось пішло не так. Спробуй ще раз пізніше."