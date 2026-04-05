import requests
import os
from dotenv import load_dotenv

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

Ai_model = "qwen/qwen3.6-plus:free"

# topics
topics = ""


def get_news_topic():
    topic = os.getenv("TOPIC")

    if topic and topic.strip():
        print("Using topic from webhook:", topic)
        return topic

    print("Using AI topic (scheduled run)")
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
            ],
            "max_tokens": 20,
            "temperature": 0.7
        }

        response = requests.post(url, headers=headers, json=payload)
        data = response.json()

        # Debug print (very useful)
        if "choices" not in data:
            print("OpenRouter Raw Response:", data)
            return "india breaking news"  # fallback

        topic = data["choices"][0]["message"]["content"].strip()
        return topic

    except Exception as e:
        print("OpenRouter Error:", e)
        return "india breaking news"  # fallback





def get_news():

    #topic = get_news_topic()
    topic = "india"

    print("Fetching news for topic:", topic)

    query = " AND ".join(topic.split())

    params = {
        "q": query,
        "language": "en",
        "pageSize": 5,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY
    }

    response = requests.get("https://newsapi.org/v2/everything", params=params)
    data = response.json()

    if "articles" in data and len(data["articles"]) > 0:

        article = data["articles"][0]

        description = article.get("description") or ""
        content = article.get("content") or ""
        source = article["source"]["name"]

        return {
            "title": article["title"],
            "image": article["urlToImage"],
            "category": topic,
            "source":source,
            "description": article["description"]
        }

    else:
        print("News API Error:", data)

        return {
            "title": article["title"],
            "description": article.get("description"),
            "image": article["urlToImage"],
            "category": topic
        }

def generate_instagram_title(description):
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
Create a catchy Instagram-style news headline from this description:

{description}

Rules:
- Make it engaging and scroll-stopping
- Max 10 to 12 words
- No hashtags
- Output ONLY the title
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
