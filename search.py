import requests

url = "https://api.parallel.ai/v1beta/search"


def _format_topics(topics):
    return ", ".join(topics)


def _format_prompt(place, topics):
    topic_sections = "\n".join([f"- {topic}" for topic in topics])
    return (
        f"Write a comprehensive, well-structured summary about {place['name']} focused on the following topics:\n"
        f"{topic_sections}\n"
        f"For each topic, provide several informative paragraphs or bullet points. "
        f"Avoid real estate listings, sales info, or overly specific property data. "
        f"Be thorough, relevant, and avoid repetition."
    )



def search_location(place, topics: list):
    """
    Returns a list of dicts, each with 'topic' and 'summary', for the user-specified topics about a place.
    Each topic is covered in detail if possible. If no info is found for a topic, summary is an empty string.
    """
    prompt = _format_prompt(place, topics)
    payload = {
        "objective": prompt,
        "processor": "base",
        "max_results": 3,
        "max_chars_per_result": 6000
    }
    headers = {
        "x-api-key": "OQK3yGFJryRnfblOgK6LSbFh0ztbmnfMjEGwkF1l",
        "Content-Type": "application/json"
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        results = response.json()
        texts = [
            " ".join(r.get("excerpts", []))
            for r in results.get("results", [])
            if r.get("excerpts")
        ]
        merged = "\n\n".join(texts)
        return merged
    except Exception as e:
        return [{"topic": topic, "summary": f"An error occurred: {e}"} for topic in topics]
