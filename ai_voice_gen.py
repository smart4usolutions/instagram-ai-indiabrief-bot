import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
WAVESPEED_API_KEY = os.getenv("WAVESPEED_API_KEY")
print("WAVESPEED API KEY PRESENT:", bool(WAVESPEED_API_KEY))


def generate_ai_audio(script_text, output_file):
    print("WAVESPEED API KEY PRESENT:", bool(WAVESPEED_API_KEY))

    submit_url = "https://api.wavespeed.ai/api/v3/elevenlabs/turbo-v2.5"

    headers = {
        "Authorization": f"Bearer {WAVESPEED_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
    "text": script_text,
    "voice_id": "Jessica",
    "model_id": "elevenlabs/turbo-v2.5",   # 👈 ADD THIS LINE
    "model_settings": {
        "stability": 0.45,
        "similarity_boost": 0.8
        }
    }

    try:
        # STEP 1: Submit job
        response = requests.post(submit_url, headers=headers, json=payload)

        if response.status_code != 200:
            print("❌ Submit Error:", response.text)
            return False

        task_id = response.json()["data"]["id"]
        print("🟡 Task ID:", task_id)

        # STEP 2: Poll result
        result_url = f"https://api.wavespeed.ai/api/v3/predictions/{task_id}/result"

        for _ in range(30):
            time.sleep(3)

            result = requests.get(result_url, headers=headers)
            data = result.json()

            if data.get("data", {}).get("outputs"):
                audio_url = data["data"]["outputs"][0]
                print("✅ Audio URL:", audio_url)

                # STEP 3: Download file
                audio_data = requests.get(audio_url).content

                with open(output_file, "wb") as f:
                    f.write(audio_data)

                print("✅ Saved:", output_file)
                return True

            print("⏳ Waiting for audio...")

        print("❌ Timeout: Audio not ready")
        return False

    except Exception as e:
        print("❌ Exception:", e)
        return False
