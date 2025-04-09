import logging
from services.text_messages import INITIAL_WHISPER_PROMPT

_model = None  # global lazy cache

def get_model():
    global _model
    if _model is None:
        import whisper  # lazy import
        _model = whisper.load_model("small")
    return _model

def transcribe_voice(wav_file: str) -> str:
    """
    Transcribes a given WAV audio file using OpenAI Whisper.
    Loads the model only on first use.
    """

    try:
        model = get_model()

        result = model.transcribe(
            wav_file,
            fp16=False,
            language="auto",
            initial_prompt=INITIAL_WHISPER_PROMPT
        )

        text = result["text"].strip()
        detected_lang = result.get("language")

        if detected_lang != "uk":
            logging.info(f"Whisper detected language: {detected_lang}, expected: 'uk'")

        return text

    except Exception as e:
        logging.error(f"Whisper transcription error: {e}")
        return ""