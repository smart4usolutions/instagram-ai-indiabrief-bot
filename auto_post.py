from news_fetcher import get_news
from ai_writer import generate_instagram_content
from ai_writer import generate_caption
from image_creator_copy import create_post_image
from upload_image import upload_image
from instagram_post import post_to_instagram
import time
import sys

def format_instagram_metadata(result):
    keywords = result.get("keywords", [])
    hashtags = result.get("hashtags", [])

    keyword_text = ", ".join(keywords)
    hashtag_text = " ".join(hashtags)

    formatted = f"""Keywords:
{keyword_text}

Hashtags:
{hashtag_text}
"""

    return formatted



#Get Newws
news = get_news()
title = news["title"]
description = news.get("description")

#Generate Instagram containt
Result = generate_instagram_content(description)

#Clean the keywords and Hashtags
pretty_output = format_instagram_metadata(Result)

#Generate Static Caption with dynamic keywords and hashtags
caption = generate_caption(
    Result["title"],
    news.get("description"),
    Result["category"],
    news["source"],
    pretty_output
)
print(caption)

if not news.get("image"):
    print("No image found. Stopping execution.")
    sys.exit()

image_path = create_post_image(
    title,
    news["image"],
    Result["keywords"][1],
    news.get("description"),
    Result["category"]
)
print("\nIMAGE CREATED:", image_path)

#upload image
image_url = upload_image(image_path)
print("Uploaded URL:", image_url)
time.sleep(5)

#Post to Instagram
post_to_instagram(image_url, caption)