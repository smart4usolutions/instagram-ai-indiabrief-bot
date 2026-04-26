from news_fetcher import get_news
from news_fetcher import generate_reel_script
from ai_voice_gen import generate_ai_audio
import subprocess
import os
import time
import sys

os.makedirs("audio", exist_ok=True)
# os.makedirs("videos", exist_ok=True)
# os.makedirs("data", exist_ok=True)

#----------------------------------
#Get News
#----------------------------------

news = get_news()
print("\nNEWS:", news["title"])
print("\nNEWS:", news["description"])
#Generate Raw Script
MAX_RETRIES = 3
success = False
for attempt in range(1, MAX_RETRIES + 1):
    print(f"🔁 Attempt {attempt}")
    script_text = generate_reel_script(news["title"],news["description"])
    print("\nNews Script:", script_text)
    if script_text != "":
        print(f"✅ Success")
        success = True
        break
    else:
        print(f"❌ Failed attempt {attempt}")
        time.sleep(3)  # small delay before retry

#----------------------------------
#Generate Voice
#----------------------------------

output_file = f"audio/reel.mp3"

#Voice generate using ai model
voice = generate_ai_audio(script_text, output_file)
if not voice:
    print(f"❌ Failed to generate audio")
print(f"✅ Audio created: {output_file}")

