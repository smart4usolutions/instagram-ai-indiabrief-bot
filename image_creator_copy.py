import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import textwrap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH = 1080
HEIGHT = 1350


# ----------------------------
# LOAD IMAGE
# ----------------------------
def load_image(image_url):
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(image_url, headers=headers, timeout=10)

        if response.status_code != 200:
            raise Exception("Bad response")

        return Image.open(BytesIO(response.content)).convert("RGB")

    except:
        return Image.new("RGB", (WIDTH, HEIGHT), (30, 30, 30))


# ----------------------------
# RESIZE IMAGE (COVER)
# ----------------------------
def resize_cover(image, target_width, target_height):
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        new_width = target_width
        new_height = int(new_width / img_ratio)

    image = image.resize((new_width, new_height), Image.LANCZOS)

    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2

    return image.crop((left, top, left + target_width, top + target_height))


# ----------------------------
# ADD CIRCLE IMAGE
# ----------------------------
def add_circle_image(canvas, image_url):
    try:
        img = load_image(image_url)
        img = resize_cover(img, 200, 200)

        mask = Image.new("L", (200, 200), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 200, 200), fill=255)

        circle = Image.new("RGBA", (200, 200))
        circle.paste(img, (0, 0), mask)

        canvas.paste(circle, (WIDTH - 240, 40), mask)
    except:
        pass


# ----------------------------
# MAIN FUNCTION
# ----------------------------
def create_post_image(title, image_url, category, inset_url=None):

    # ----------------------------
    # BASE CANVAS
    # ----------------------------
    canvas = Image.new("RGB", (WIDTH, HEIGHT), (0, 0, 0))
    draw = ImageDraw.Draw(canvas)

    # ----------------------------
    # MAIN IMAGE
    # ----------------------------
    main_img = load_image(image_url)
    # ----------------------------
    # IMAGE WITH PADDING (LIKE REF)
    # ----------------------------
    padding_x = 60
    padding_top = 60

    img_width = WIDTH - (padding_x * 2)
    img_height = int(HEIGHT * 0.5)

    main_img = resize_cover(main_img, img_width, img_height)

    # Position
    img_x = padding_x
    img_y = padding_top

    canvas.paste(main_img, (img_x, img_y))

    # ----------------------------
    # WHITE BORDER (OUTSIDE IMAGE)
    # ----------------------------
    border_thickness = 10

    draw.rectangle(
        [
            img_x - border_thickness,
            img_y - border_thickness,
            img_x + img_width + border_thickness,
            img_y + img_height + border_thickness
        ],
        outline="white",
        width=border_thickness
    )


    # ----------------------------
    # INSET IMAGE
    # ----------------------------
    if inset_url:
        add_circle_image(canvas, inset_url)

    # ----------------------------
    # FONTS
    # ----------------------------
    font_bold_path = os.path.join(BASE_DIR, "fonts/ARIALBD.TTF")
    font_regular_path = os.path.join(BASE_DIR, "fonts/ARIAL.TTF")

    try:
        font_category = ImageFont.truetype(font_bold_path, 40)
        font_headline_big = ImageFont.truetype(font_bold_path, 60)
        font_headline_small = ImageFont.truetype(font_bold_path, 52)
        font_footer = ImageFont.truetype(font_regular_path, 32)
    except:
        font_category = ImageFont.load_default()
        font_headline_big = ImageFont.load_default()
        font_headline_small = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    # ----------------------------
    # CATEGORY TAG
    # ----------------------------
    category_text = category.upper()
    cat_y = int(HEIGHT * 0.55) - 30

    draw.rectangle(
        [WIDTH // 2 - 100, cat_y, WIDTH // 2 + 100, cat_y + 50],
        fill=(0, 0, 0)
    )

    draw.text(
        (WIDTH // 2 - 50, cat_y + 8),
        category_text,
        font=font_category,
        fill=(255, 180, 0),
        align="center"
    )

    # ----------------------------
# HEADLINE SPLIT
# ----------------------------
    words = title.split()

    if len(words) > 6:
        first_line = " ".join(words[:6])
        rest_text = " ".join(words[6:])
    else:
        first_line = title
        rest_text = ""

    first_line = textwrap.fill(first_line, width=22)
    rest_text = textwrap.fill(rest_text, width=26)

    text_y = cat_y + 80

    # ----------------------------
    # CALCULATE CENTER POSITION
    # ----------------------------
    def draw_centered_multiline(draw, text, y, font, fill):
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=10)
        text_width = bbox[2] - bbox[0]

        x = (WIDTH - text_width) // 2

        draw.multiline_text(
            (x, y),
            text,
            font=font,
            fill=fill,
            spacing=10,
            align="center"
        )

        return bbox[3] - bbox[1]  # height


    # ----------------------------
    # DRAW FIRST LINE (YELLOW)
    # ----------------------------
    h1 = draw_centered_multiline(
        draw,
        first_line,
        text_y,
        font_headline_big,
        (255, 180, 0)
    )

    # ----------------------------
    # DRAW SECOND LINE (WHITE)
    # ----------------------------
    draw_centered_multiline(
        draw,
        rest_text,
        text_y + h1 + 20,
        font_headline_small,
        "white"
    )
# ----------------------------
# BOTTOM BRANDING (CENTERED & HIGHER)
# ----------------------------
    line_y = HEIGHT - 80

    draw.line(
        [(120, line_y), (WIDTH - 120, line_y)],
        fill=(80, 80, 80),
        width=2
    )

    footer_text = "@ai.indiabrief"

    bbox = draw.textbbox((0, 0), footer_text, font=font_footer)
    text_w = bbox[2] - bbox[0]

    draw.text(
        ((WIDTH - text_w) // 2, line_y + 20),
        footer_text,
        font=font_footer,
        fill="white"
    )


    # ----------------------------
    # SAVE
    # ----------------------------
    output_path = "generated_posts/post.png"
    os.makedirs("generated_posts", exist_ok=True)

    canvas.save(output_path)

    print("✅ IMAGE CREATED:", output_path)

    return output_path
create_post_image("Indian Woman Lands German Product Manager Job Without Speaking German, Stuns Social Media", "https://img.etimg.com/thumb/msid-130232485,width-1200,height-630,imgsize-2034780,overlay-economictimes/articleshow.jpg", "India")