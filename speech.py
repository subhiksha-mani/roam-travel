import os
import hashlib
from openai import OpenAI
from constants import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def text_to_speech(text):
    # Convert list to string if needed
    if isinstance(text, list):
        text = " ".join(text)

    # Ensure audio folder exists
    os.makedirs("audio", exist_ok=True)

    # Make a unique filename
    hash_digest = hashlib.md5(text.encode()).hexdigest()[:6]
    audio_file = os.path.join("audio", f"generated_{hash_digest}.mp3")

    # Call TTS API
    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    audio_bytes = response.read()

    with open(audio_file, "wb") as f:
        f.write(audio_bytes)

    return audio_file
