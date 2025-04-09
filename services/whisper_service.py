import whisper

# Load once at module level
model = whisper.load_model("small")


def transcribe_voice(wav_file: str) -> str:
    result = model.transcribe(
        wav_file,
        language="uk",
        fp16=False,
        initial_prompt="Це мама, яка ділиться своїми емоціями, радістю, тривогами, втомою або болем."
    )
    return result["text"]
