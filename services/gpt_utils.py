import logging
import os
import openai
from services.user_state import UserStateManager

# Load API key
openai.api_key = os.getenv("OPENAI_API_KEY")


def ask_gpt_with_history(state: UserStateManager, user_input: str, system_prompt: str) -> str:
    """
    Generate a GPT reply using the given state, user input, and prompt.
    Appends last 3 interactions from history for context.
    """
    topic = state.get("topic")
    history = state.get_gpt_history(topic)

    messages = [{"role": "system", "content": system_prompt}]
    for pair in history[-3:]:
        messages.append({"role": "user", "content": pair["question"]})
        messages.append({"role": "assistant", "content": pair["reply"]})
    messages.append({"role": "user", "content": user_input})

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            timeout=10  # prevent long waits or blocking
        )
        bot_reply = response["choices"][0]["message"]["content"]
        state.add_gpt_interaction(user_input, bot_reply)
        return bot_reply
    except Exception as e:
        logging.warning(f"❌ GPT error: {e}")
        raise
