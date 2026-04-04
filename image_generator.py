import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from datetime import datetime


PAGE_NAME = "@pagename"


def download_image(url):

    if url is None:
        return Image.new("RGB", (1080, 1080), "black")

    response = requests.get(url)
    img = Image.open(BytesIO(response.content))

    img = img.resize((1080, 1080))

    return img


def add_dark_overlay(img):

    overlay = Image.new("RGBA", img.size, (0, 0, 0, 120))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)

    return img


def wrap_text(text, line_length=25):

    words = text.split()
    lines = []
    current = ""

    for word in words:

        if len(current + " " + word) <= line_length:
            current += " " + word
        else:
            lines.append(current.strip())
            current = word

    lines.append(current.strip())

    return lines


def generate_image(news):

    title = news["title"]
    image_url = news["image"]
    category = news["category"].upper()

    img = download_image(image_url)

    img = add_dark_overlay(img)

    draw = ImageDraw.Draw(img)

    try:
        font_big = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # Page name
    draw.text((40, 40), PAGE_NAME, font=font_small, fill="white")

    # Date
    today = datetime.now().strftime("%d %b %Y")
    draw.text((820, 40), today, font=font_small, fill="white")

    # Category
    draw.text((80, 600), category, font=font_small, fill="white")

    # Line
    draw.line((80, 650, 600, 650), fill="white", width=5)

    # Headline
    lines = wrap_text(title.upper())

    y = 680

    for line in lines:
        draw.text((80, y), line, font=font_big, fill="white")
        y += 80

    img = img.convert("RGB")

    img.save("post.png")

    print("Image saved as post.png")
