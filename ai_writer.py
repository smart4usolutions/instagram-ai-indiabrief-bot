import requests
import os
import textwrap
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
pageName = os.getenv("PAGE_NAME")

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_caption(title, description, category, source, other):

    if not description:
        description = "Latest developments are unfolding in this story."

    # clean the text
    description = description.replace("[+", "").split("...")[0]

    # create paragraphs
    lines = textwrap.wrap(description)

    para1 = " ".join(lines[:4])
    para2 = " ".join(lines[4:8])

    caption = f"""🚨 {category.upper()} NEWS

{title}

{para1}

{para2}

📰 Source: {source}

Follow {pageName} for the latest global developments.

{other}
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

import json


def generate_instagram_content(description):
    messages = [
        {
    "role": "system",
    "content": """
Return ONLY valid JSON.

Rules:
- No markdown
- No backticks
- No explanation
- No text before JSON
- No text after JSON
- JSON must be syntactically valid
- Use double quotes only
- Arrays must be proper JSON arrays
"""
},
        {
            "role": "user",
            "content": f"""
Analyze this news and generate:

1. Viral Instagram headline
2. Category classification
3. Keywords
4. Relevant hashtags

NEWS:
{description}

HEADLINE RULES:
- 12 to 16 words
- Exactly one sentence
- Sentence case
- No hashtags
- No emojis
- Emotional and curiosity-driven
- Include at least one power word

CATEGORY:
Return exactly one:
urgent
growth
shocking
explainer

KEYWORDS RULES:
- 8 to 12 keywords
- Short phrases (1 to 3 words)

HASHTAG RULES:
- 5 to 10 hashtags
- Relevant to the news
- Trending-style if applicable
- Include # symbol
- No spaces

OUTPUT FORMAT:
{{
    "title": "headline here",
    "category": "urgent/growth/shocking/explainer",
    "keywords": ["keyword1", "keyword2"],
    "hashtags": ["#tag1", "#tag2"]
}}

Return valid JSON only.
"""
        }
    ]

    try:
        result = call_openrouter(
            messages,
            max_tokens=220,
            temperature=0.6
        )

        if result:
            data = json.loads(result)

            return {
                "title": data.get("title", generate_fallback_title(description)),
                "category": data.get("category", "shocking"),
                "keywords": data.get("keywords", generate_fallback_keywords(description)),
                "hashtags": data.get("hashtags", generate_fallback_hashtags(description))
            }

    except Exception as e:
        print("❌ Content generation error:", e)

    return {
        "title": generate_fallback_title(description),
        "category": "shocking",
        "keywords": generate_fallback_keywords(description),
        "hashtags": generate_fallback_hashtags(description)
    }


def generate_fallback_title(description):
    words = description.split()
    return " ".join(words[:14]) + "..."


def generate_fallback_keywords(description):
    words = []
    for word in description.split():
        word = word.strip(",.!?").lower()
        if len(word) > 4 and word not in words:
            words.append(word)
        if len(words) >= 8:
            break
    return words


def generate_fallback_hashtags(description):
    hashtags = []
    for word in description.split():
        word = word.strip(",.!?").lower()
        if len(word) > 4 and word.isalpha():
            hashtags.append(f"#{word}")
        if len(hashtags) >= 5:
            break
    return hashtags

def call_openrouter(messages, max_tokens=30, temperature=0.7):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    models_to_try = [
        "google/gemma-2-9b-it:free",
        "mistralai/mistral-7b-instruct:free",
        "meta-llama/llama-3-8b-instruct:free"
        "openrouter/free",
        "openrouter/free"
    ]

    for model in models_to_try:
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            print(f"Using Model: {model}")
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            data = response.json()

            # ✅ Safe extraction
            if "choices" in data and len(data["choices"]) > 0:
                content = data["choices"][0]["message"].get("content")

                if content and content.strip():
                    return content.strip()
                else:
                    print(f"⚠️ Empty content from {model}")

            else:
                print(f"⚠️ Invalid response from {model}: {data}")

        except Exception as e:
            print(f"❌ Model failed: {model} | Error: {e}")

    return None  # All models failed


