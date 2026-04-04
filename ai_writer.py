import requests
import os
import textwrap
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENROUTER_API_KEY")
pageName = os.getenv("PAGE_NAME")

def generate_caption(title, description, category, source):

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

#news #breakingnews #{category.lower()} #worldnews #trending #dailynews
"""

    return caption
