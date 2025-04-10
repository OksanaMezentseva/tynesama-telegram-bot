import os
import openai
import logging

# Optional: only load .env if running locally
if os.environ.get("ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

# Get key from env (whether local or Render)
openai.api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = (
    "You are a gentle, supportive assistant for tired moms. "
    "Respond briefly, warmly, and with empathy."
)

def ask_gpt(user_input: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            timeout=10  # prevent long hanging
        )
        reply = response["choices"][0]["message"]["content"]
        logging.info("🧠 GPT responded successfully")
        return reply

    except Exception as e:
        logging.warning(f"❌ GPT error: {e}")
        return "Вибач, зараз я не можу відповісти. Спробуй трохи пізніше 💛"