from openai import OpenAI

from constants import OPENAI_API_KEY

client = OpenAI(api_key=OPENAI_API_KEY)

from search import _format_topics

def get_script(chunks, place, topics):
    formatted_topics = _format_topics(topics)
    response = client.chat.completions.create(model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful travel companion."},
        {"role": "user", "content": f"Explain the {formatted_topics} for {place["name"]}. This is the provided context: {chunks}"}
    ])

    return response.choices[0].message.content

