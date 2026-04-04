import requests
import os

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
IG_USER_ID = os.getenv("IG_USER_ID")

def post_to_instagram(image_url, caption):

    # Create container
    url = f"https://graph.instagram.com/v19.0/{IG_USER_ID}/media"

    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": ACCESS_TOKEN
    }

    res = requests.post(url, data=payload).json()
    creation_id = res.get("id")
    if not creation_id:
        print("❌ Error creating container:", res)
        return

    print("Container:", res)

    import time
    time.sleep(15)

    # Publish
    publish_url = f"https://graph.instagram.com/v19.0/{IG_USER_ID}/media_publish"

    publish_payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }

    publish_res = requests.post(publish_url, data=publish_payload).json()

    print("Published:", publish_res)
    print("✅ Image Posted Successfully")
