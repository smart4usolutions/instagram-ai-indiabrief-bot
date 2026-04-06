from news_fetcher import get_news
from news_fetcher import generate_instagram_title
from ai_writer import generate_caption
from image_creator import create_post_image
from upload_image import upload_image
from instagram_post import post_to_instagram
import time
import sys

news = get_news()

insta_title = generate_instagram_title(news.get("description"))
if insta_title != "Breaking News Update":
    title = insta_title
else:
    title = news["title"]


print("\nNEWS:", news["title"])
print("\nInsta Title:", title)
print("\nDISC:", news.get("description"))
time.sleep(5)


caption = generate_caption(
    news["title"],
    news.get("description"),
    news["category"],
    news["source"]
)

print("\nINSTAGRAM CAPTION:\n")
print(caption)
time.sleep(5)

if not news.get("image"):
    print("No image found. Stopping execution.")
    sys.exit()
image_path = create_post_image(
    #news["title"],
    title,
    news["image"],
    news["category"]
)

print("\nIMAGE CREATED:", image_path)
time.sleep(5)

#upload image
image_url = upload_image(image_path)
print("Uploaded URL:", image_url)
time.sleep(5)

#Post to Instagram
#post_to_instagram(image_url, caption)