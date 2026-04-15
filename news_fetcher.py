import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# -----------------------------
# 🔁 Reusable OpenRouter Caller
# -----------------------------
def call_openrouter(messages, max_tokens=30, temperature=0.7):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    # models_to_try = [
    #     "z-ai/glm-4.5-air:free",
    #     "arcee-ai/trinity-large-preview:free",
    #     "google/gemma-4-26b-a4b-it:free",
    #     "stepfun/step-3.5-flash:free",
    #     "nvidia/nemotron-3-super-120b-a12b:free"
    # ]
    models_to_try = [
        "openrouter/free",
        "openrouter/free",
        "openrouter/free",
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

            response = requests.post(url, headers=headers, json=payload, timeout=15)
            data = response.json()

            if "choices" in data:
                return data["choices"][0]["message"]["content"].strip()
            else:
                print(f"⚠️ Invalid response from {model}:", data)

        except Exception as e:
            print(f"❌ Model failed: {model} | Error: {e}")

    return None  # All models failed


# -----------------------------
# 📰 Get Trending Topic
# -----------------------------
def get_news_topic():
    topic = os.getenv("TOPIC")

    if topic and topic.strip():
        print("Using topic from webhook:", topic)
        return topic

    print("Using AI topic (scheduled run)")

    messages = [
        {
            "role": "system",
            "content": "You are a real-time news trend detector."
        },
        {
            "role": "user",
            "content": """
Identify the most important current trending news topic in India.

Generate a concise search query for a news API.

Rules:
- Focus on recent or breaking topics
- Use specific keywords (events, places, names)
- Keep it 3 to 4 words
- Output ONLY the query (no explanation)
"""
        }
    ]

    try:
        topic = call_openrouter(messages, max_tokens=20, temperature=0.7)

        if topic:
            return topic

        print("⚠️ All models failed, using fallback")
        return "india breaking news"

    except Exception as e:
        print("OpenRouter Error:", e)
        return "india breaking news"


# -----------------------------
# 📰 Fetch News
# -----------------------------
def get_news():
    #topic = get_news_topic()   # ✅ now uses AI + fallback
    topic = "India"
    print("📰Fetching news for topic:", topic)

    query = " AND ".join(topic.split())

    params = {
        "q": query,
        "language": "en",
        "pageSize": 5,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY
    }

    try:
        response = requests.get("https://newsapi.org/v2/everything", params=params, timeout=10)
        data = response.json()

        if "articles" in data and len(data["articles"]) > 0:

            article = data["articles"][0]

            # fallback if no image
            if not article.get("urlToImage") and len(data["articles"]) > 1:
                article = data["articles"][1]

            return {
                "title": article.get("title"),
                "image": article.get("urlToImage"),
                "category": topic,
                "source": article.get("source", {}).get("name"),
                "description": article.get("description") or ""
            }

        else:
            print("⚠️ News API returned no articles:", data)

            return {
                "title": "No news found",
                "description": "",
                "image": None,
                "category": topic,
                "source": ""
            }

    except Exception as e:
        print("❌ News API Error:", e)

        return {
            "title": "Error fetching news",
            "description": "",
            "image": None,
            "category": topic,
            "source": ""
        }


# -----------------------------
# 📱 Generate Instagram Title
# -----------------------------
def generate_instagram_title(description):
    messages = [
        {
            "role": "system",
            "content": "You write viral, high-engagement Instagram news headlines."
        },
        {
            "role": "user",
            "content": f"""
Turn this news into a VIRAL Instagram headline:

{description}

STRICT RULES:
- Max 12–16 words
- Use POWER words (shocking, massive, big, huge, exposed, unbelievable, etc.)
- Create curiosity or tension
- Make it sound emotional or surprising
- Avoid boring/news tone
- NO hashtags
- NO emojis
- Use sentence case

STYLE EXAMPLES:
- "This decision could change everything for Indian voters"
- "Massive update just dropped and people are shocked"
- "This move by the government is raising serious questions"

Output ONLY the headline.
"""
        }
    ]

    try:
        for _ in range(2):  # try 2 times
            title = call_openrouter(messages, max_tokens=40, temperature=1)
            if title:
                return title

        if title and len(title.split()) > 4:
            return title.strip()

        # fallback
        return generate_fallback_title(description)

    except Exception as e:
        print("❌ Title generation error:", e)
        return generate_fallback_title(description)
    
    
def generate_fallback_title(description):
    text = description.strip()

    # Take first strong sentence
    if "." in text:
        text = text.split(".")[0]

    words = text.split()

    # shorten
    short = " ".join(words[:14])

    return short + "..."
