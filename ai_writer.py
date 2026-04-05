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

#news #breakingnews #{category.lower()} #indianews #trending #dailynews
"""

    return caption

Ai_model = "qwen/qwen3.6-plus:free"

def generate_instagram_keywords(description):
    try:
        url = "https://openrouter.ai/api/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": Ai_model,
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

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        title = data["choices"][0]["message"]["content"].strip()

        return title

    except Exception as e:
        print("Title generation error:", e)
        return "Breaking News Update"