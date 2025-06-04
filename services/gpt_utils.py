import logging
import os
import openai
from services.user_state import UserStateManager
from prompts.system_prompts import PROMPTS_BY_TOPIC

# Load API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")


async def ask_gpt_with_history(state: UserStateManager, user_input: str) -> str:
    """
    Generate a GPT reply asynchronously, personalizing the response
    based on the user's profile stored in the state.
    The profile summary is added to the system prompt in a friendly, empathetic manner.
    """
    topic = state.get("topic", "general")
    base_prompt = PROMPTS_BY_TOPIC.get(topic, PROMPTS_BY_TOPIC["general"])
    history = state.get_gpt_history(topic)
    profile = state.get("profile", {})

    # Build a friendly English summary of the user's profile
    summary_parts = []

    if profile.get("status"):
        summary_parts.append(
            f"You are talking to a mother who reported her status as: {profile['status'].lower()}."
        )

    if profile.get("children_count"):
        summary_parts.append(
            f"She has {profile['children_count']} child(ren)."
        )

    if profile.get("children_ages"):
        summary_parts.append(
            f"The children are approximately: {profile['children_ages']} old."
        )

    # We do not include 'preferred_topics' here based on current requirements

    # Combine all parts into one friendly profile summary
    profile_summary = " ".join(summary_parts)

    # Combine profile summary with the base system prompt
    system_prompt = f"{profile_summary} {base_prompt}".strip()

    # Build messages for GPT API: system prompt + recent conversation + user input
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
        # Save interaction to history for future context
        state.add_gpt_interaction(user_input, bot_reply)
        return bot_reply

    except Exception as e:
        logging.warning(f"❌ GPT error: {e}")
        # Friendly fallback message for user
        return (
            "На жаль, я зараз не можу дати відповідь 😔 "
            "Спробуй, будь ласка, ще раз трохи пізніше."
        )