import requests
import os

CLOUD_NAME = os.getenv("CLOUD_NAME")
UPLOAD_PRESET = os.getenv("UPLOAD_PRESET")

def upload_image(image_path):
    url = f"https://api.cloudinary.com/v1_1/{CLOUD_NAME}/image/upload"

    with open(image_path, "rb") as file:
        files = {"file": file}
        data = {"upload_preset": UPLOAD_PRESET}

        response = requests.post(url, files=files, data=data)
        res = response.json()

    return res["secure_url"]