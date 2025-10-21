from openai import OpenAI
from constants import OPENAI_API_KEY


def clean_text(text: str, topics: list) -> str:
    """
    Clean text for LLM ingestion: remove HTML, URLs, and repetitive navigation/noise.
    """

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = f"""
    You are a helpful assistant. Extract the main readable content from the text below.
    Remove navigation links, repeated headers, ads, HTML tags, markdown links, and any noisy artifacts.
    Return only clean, readable paragraphs. Break down each section with the relevant topic: {topics}

    Input:
    {text}
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content.strip()