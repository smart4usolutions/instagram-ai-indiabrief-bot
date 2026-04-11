import requests
import os
import textwrap
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
pageName = os.getenv("PAGE_NAME")

def generate_caption(title, description, category, source):

    if not description:
        description = "Latest developments are unfolding in this story."

    # clean the text
    description = description.replace("[+", "").split("...")[0]

    # create paragraphs
    lines = textwrap.wrap(description)

    para1 = " ".join(lines[:4])
    para2 = " ".join(lines[4:8])

    keywords = generate_instagram_keywords(description)

    caption = f"""🚨 {category.upper()} NEWS

{title}

{para1}

{para2}

📰 Source: {source}

Follow {pageName} for the latest global developments.

Keyword: {keywords}

#news #breakingnews #india #indianews #trending #dailynews
"""

    return caption


def generate_instagram_keywords(description):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    models_to_try = [
        "z-ai/glm-4.5-air:free",
        "arcee-ai/trinity-large-preview:free",
        "google/gemma-4-26b-a4b-it:free",
        "stepfun/step-3.5-flash:free",
        "nvidia/nemotron-3-super-120b-a12b:free"
    ]

    for model in models_to_try:
        try:
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are an expert social media copywriter."
                    },
                    {
                        "role": "user",
                        "content": f"""
Extract relevant keywords from the given news article.
Rules:
Output only keywords (no extra text)
Provide 8 to 12 keywords
Use short phrases (1 to 3 words)
Separate with commas
Avoid generic words

{description}
"""
                    }
                ],
                "max_tokens": 30,
                "temperature": 0.9
            }

            response = requests.post(url, headers=headers, json=payload, timeout=15)

            # Raise error for bad HTTP status
            response.raise_for_status()

            data = response.json()

            # Validate response structure
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"]["content"].strip()

                # Ensure non-empty result
                if content:
                    print(f"✅ Success with model: {model}")
                    return content

        except Exception as e:
            print(f"❌ Model failed: {model} | Error: {e}")

    # Final fallback
    return "India News Updates"
