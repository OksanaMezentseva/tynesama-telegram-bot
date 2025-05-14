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
    Adds profile summary (in English) to the system prompt for personalization.
    """
    topic = state.get("topic", "general")
    base_prompt = PROMPTS_BY_TOPIC.get(topic, PROMPTS_BY_TOPIC["general"])
    history = state.get_gpt_history(topic)
    profile = state.get("profile", {})

    # Build English summary of the user's profile
    summary_parts = []

    if profile.get("status"):
        summary_parts.append(f"The user reported their status as: {profile['status'].lower()}.")

    if profile.get("children_count"):
        summary_parts.append(f"She has {profile['children_count']} children.")

    if profile.get("children_ages"):
        summary_parts.append(f"Their ages are: {profile['children_ages']}.")

    if profile.get("breastfeeding"):
        summary_parts.append(f"Breastfeeding status: {profile['breastfeeding'].lower()}.")

    if profile.get("country"):
        summary_parts.append(f"She currently lives in: {profile['country'].lower()}.")

    profile_summary = " ".join(summary_parts)

    # Combine with system prompt
    system_prompt = f"{profile_summary} {base_prompt}".strip()

    # Construct messages list
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