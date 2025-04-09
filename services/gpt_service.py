import os
import openai

# Optional: only load .env if running locally
if os.environ.get("ENV") != "production":
    from dotenv import load_dotenv
    load_dotenv()

# Get key from env (whether local or from Render)
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
            timeout=10  # optional: prevent hanging forever
        )
        return response["choices"][0]["message"]["content"]
    except Exception as e:
        # You could also log the exception here
        return "Вибач, зараз я не можу відповісти. Спробуй трохи пізніше 💛"