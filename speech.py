import datetime
import hashlib
import os
from openai import OpenAI
from constants import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

def text_to_speech(text: str, landmark_name: str):
    hash_digest = hashlib.md5(text.encode()).hexdigest()[:6]
    safe_name = landmark_name.replace(" ", "_")
    audio_file = os.path.join("audio", f"{safe_name}_{hash_digest}.mp3")

    response = client.audio.speech.create(
        model="gpt-4o-mini-tts",
        voice="alloy",
        input=text
    )
    audio_bytes = response.read()

    with open(audio_file, "wb") as f:
        f.write(audio_bytes)

    return audio_file