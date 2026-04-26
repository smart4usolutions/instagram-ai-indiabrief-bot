import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")


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



    messages = [
        {
            "role": "system",
            "content": "You are a strict classifier. You ONLY return one word."
        },
        {
            "role": "user",
            "content": f"""
Classify this news into EXACTLY one category:

urgent
growth
shocking
explainer

Definitions:
- urgent = breaking news, government, accidents, immediate updates
- growth = business, stocks, economy, money
- shocking = unexpected, controversy, surprising events
- explainer = analysis, why it matters, deeper meaning

RULES:
- Output ONLY ONE WORD from the list above
- Do NOT explain
- Do NOT add anything else
- If unsure, choose the closest match

News:
{description}
"""
        }
    ]

    result = call_openrouter(messages, max_tokens=5, temperature=0)

    if result:
        cleaned = result.strip().lower()

        # strict filtering
        if cleaned in ["urgent", "growth", "shocking", "explainer"]:
            return cleaned

    return "shocking"  # safe fallback

def generate_reel_script(title,description):
    messages = [
        {
            "role": "system",
            "content": """You are a viral Instagram reel script writer."""
        },
        {
            "role": "user",
            "content": f"""
Create a 60-second Hinglish news reel script in a conversational tone that maximize watch time and retention..
Use natural Hinglish like how people speak on Instagram.
Use maximum Hindi and Some what English where needed or fits
Keep sentences short, simple, and powerful.
Avoid boring or robotic language.
Make the hook very strong and curiosity-driven.

Structure:
Hook,Context,Main,Impact,CTA

Rules:
- Start with a strong hook (curiosity or shock)
- Use simple Hinglish (mix of Hindi + English)
- Keep sentences short
- Make it engaging and easy to listen
- No emojis
- No hashtags
- No bullet points
- Just Ready to read script 
- No Notes, NO follow back questions, No suggestions notthing just pure script
- Without keywords like Hook,Context,Main,Impact,CTA



News:
Title: {title}
Description: {description}
"""
        }
    ]

    try:
        for _ in range(2):  # try 2 times
            script = call_openrouter(messages, max_tokens=400, temperature=0.6)
            if script:
                return script

    except Exception as e:
        print("❌ Script generation error:", e)
