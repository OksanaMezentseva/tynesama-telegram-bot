import logging
import os
import openai
from services.user_state import UserStateManager
from prompts.system_prompts import PROMPTS_BY_TOPIC

# Load API key
openai.api_key = os.getenv("OPENAI_API_KEY")


async def ask_gpt_with_history(state: UserStateManager, user_input: str) -> str:
    """
    Asynchronously generate a GPT reply using the given state and user input.
    Selects the appropriate system prompt based on current topic.
    Appends last 3 interactions from history for context.
    """
    topic = state.get("topic", "general")
    system_prompt = PROMPTS_BY_TOPIC.get(topic, PROMPTS_BY_TOPIC["general"])
    history = state.get_gpt_history(topic)

    messages = [{"role": "system", "content": system_prompt}]
    for pair in history[-3:]:
        messages.append({"role": "user", "content": pair["question"]})
        messages.append({"role": "assistant", "content": pair["reply"]})
    messages.append({"role": "user", "content": user_input})

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=300,
            temperature=0.7,
            timeout=10
        )

        bot_reply = response["choices"][0]["message"]["content"]
        state.add_gpt_interaction(user_input, bot_reply)
        return bot_reply

    except Exception as e:
        logging.warning(f"❌ GPT error: {e}")
        return (
            "На жаль, я зараз не можу дати відповідь 😔 "
            "Спробуй, будь ласка, ще раз трохи пізніше."
        )