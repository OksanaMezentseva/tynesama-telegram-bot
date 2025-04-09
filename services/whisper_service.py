import whisper
import logging
from services.text_messages import INITIAL_WHISPER_PROMPT

# Load Whisper model once globally
model = whisper.load_model("small")

def transcribe_voice(wav_file: str) -> str:
    """
    Transcribes a given WAV audio file using OpenAI Whisper.
    Automatically detects the language and returns the recognized text.
    Logs any errors and returns an empty string if transcription fails.
    """

    try:
        # Transcribe the audio file
        result = model.transcribe(
            wav_file,
            fp16=False,
            language="auto",  # auto-detect language (e.g. UA or RU)
            initial_prompt=INITIAL_WHISPER_PROMPT
        )

        text = result["text"].strip()
        detected_lang = result.get("language")

        # Optional: Log language detection result
        if detected_lang != "uk":
            logging.info(f"Whisper detected language: {detected_lang}, expected: 'uk'")

        return text

    except Exception as e:
        logging.error(f"Whisper transcription error: {e}")
        return ""