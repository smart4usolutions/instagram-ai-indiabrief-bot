import os
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import textwrap

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WIDTH = 1080
HEIGHT = 1350  # Instagram 4:5


# ----------------------------
# RESIZE IMAGE (NO STRETCH)
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
# LOAD IMAGE (ROBUST)
# ----------------------------
def load_image(image_url):
    try:
        print("IMAGE URL:", image_url)

        if not image_url:
            raise Exception("Empty image URL")

        headers = {"User-Agent": "Mozilla/5.0"}

        response = requests.get(
            image_url,
            headers=headers,
            timeout=10,
            allow_redirects=True
        )

        if response.status_code != 200:
            raise Exception("Bad response")

        img = Image.open(BytesIO(response.content)).convert("RGB")
        print("✅ Image loaded")

        output_path = "generated_posts/raw_img.png"
        os.makedirs("generated_posts", exist_ok=True)
        img.save(output_path)

        print("✅ RAW IMAGE SAVED:", output_path)

    except Exception as e:
        print("❌ Image load failed:", e)
        img = Image.new("RGB", (WIDTH, HEIGHT), (20, 20, 20))

    return img


# ----------------------------
# STRONG BOTTOM GRADIENT
# ----------------------------
def apply_bottom_gradient(image):
    gradient = Image.new("L", (1, HEIGHT))

    for y in range(HEIGHT):
        if y < HEIGHT * 0.4:
            value = 0
        else:
            value = int(255 * ((y - HEIGHT * 0.4) / (HEIGHT * 0.6)))
            

        gradient.putpixel((0, y), value)

    alpha = gradient.resize((WIDTH, HEIGHT))
    black = Image.new("RGB", (WIDTH, HEIGHT), (25, 10, 10))

    return Image.composite(black, image, alpha)


# ----------------------------
# TEXT WRAP
# ----------------------------
def wrap_text(text, max_chars): 
    lines = [] 
    for line in text.split("\n"): 
        lines.extend(textwrap.wrap(line, width=max_chars)) 
    return "\n".join(lines)


# ----------------------------
# DYNAMIC FONT
# ----------------------------
def get_dynamic_font(text, font_path, max_width, max_size=80, min_size=30):
    for size in range(max_size, min_size, -2):
        font = ImageFont.truetype(font_path, size)
        bbox = font.getbbox(text)
        text_width = bbox[2] - bbox[0]

        if text_width <= max_width:
            return font

    return ImageFont.truetype(font_path, min_size)


#-----------------------------
#Smart Fit
#-----------------------------
def smart_fit_image(image, target_width, target_height):
    # ----------------------------
    # 1. CREATE BLURRED BACKGROUND
    # ----------------------------
    bg = resize_cover(image, target_width, target_height)
    bg = bg.filter(ImageFilter.GaussianBlur(13))

    # Slight dark overlay for text readability
    overlay = Image.new("RGBA", (target_width, target_height), (0, 0, 0, 120))
    bg = bg.convert("RGBA")
    bg = Image.alpha_composite(bg, overlay)

    # ----------------------------
    # 2. RESIZE FOREGROUND (FIT)
    # ----------------------------
    img_ratio = image.width / image.height
    target_ratio = target_width / target_height

    if img_ratio > target_ratio:
        # Fit by width
        new_width = target_width - 100  # padding
        new_height = int(new_width / img_ratio)
    else:
        # Fit by height
        new_height = target_height - 200  # space for text
        new_width = int(new_height * img_ratio)

    fg = image.resize((new_width, new_height), Image.LANCZOS)

    # ----------------------------
    # 3. CENTER IMAGE
    # ----------------------------
    x = (target_width - new_width) // 2
    y = (target_height - new_height) // 2 - 200  # slight upward bias

    bg.paste(fg, (x, y))

    return bg.convert("RGB")


# ----------------------------
# MAIN FUNCTION
# ----------------------------
def create_post_image(title, image_url, category):

    # Load & prepare image
    bg = load_image(image_url)
    # bg = resize_cover(bg, WIDTH, HEIGHT)
    # bg = bg.filter(ImageFilter.GaussianBlur(2))
    bg = smart_fit_image(bg, WIDTH, HEIGHT)
    bg = apply_bottom_gradient(bg)
    bg = apply_bottom_gradient(bg)

    draw = ImageDraw.Draw(bg)

    # Fonts (SAFE LOAD)
    font_bold_path = os.path.join(BASE_DIR, "fonts/ARIALBD.TTF")
    font_regular_path = os.path.join(BASE_DIR, "fonts/ARIAL.TTF")

    try:
        font_page = ImageFont.truetype(font_bold_path, 42)
        font_category = ImageFont.truetype(font_bold_path, 50)
    except:
        print("⚠️ Font load failed, using default")
        font_page = ImageFont.load_default()
        font_category = ImageFont.load_default()

    # ----------------------------
    # PAGE NAME (TOP CENTER)
    # ----------------------------
    page_name = "Follow " + str(os.getenv("PAGE_NAME"))

    bbox = draw.textbbox((0, 0), page_name, font=font_page)
    text_width = bbox[2] - bbox[0]

    x = (WIDTH - text_width) // 2
    y = 30

    draw.text((x+2, y+2), page_name, font=font_page, fill="black")
    draw.text((x, y), page_name, font=font_page, fill="white")

    # ----------------------------
    # TEXT PREP
    # ----------------------------
    title = wrap_text(title, 18 if len(title) > 60 else 22)

    max_width = WIDTH - 120
    max_total_height = int(HEIGHT * 0.40)

    bottom_padding = 80
    gap = 30

    # CATEGORY SIZE
    #category_text = category.upper()
    category_text = "Daily Updates"

    cat_bbox = draw.textbbox((0, 0), category_text, font=font_category)
    cat_text_w = cat_bbox[2] - cat_bbox[0]
    cat_text_h = cat_bbox[3] - cat_bbox[1]

    padding_x = 40
    padding_y = 20

    box_w = cat_text_w + padding_x * 2
    box_h = cat_text_h + padding_y * 2

    # Available space for title
    available_title_height = max_total_height - box_h - gap

    # ----------------------------
    # SMART FONT SCALING (STRICT)
    # ----------------------------
    best_font = None

    for size in range(90, 30, -2):
        try:
            font = ImageFont.truetype(font_bold_path, size)
        except:
            font = ImageFont.load_default()

        title_bbox = draw.multiline_textbbox(
            (0, 0), title, font=font, spacing=12
        )

        title_w = title_bbox[2] - title_bbox[0]
        title_h = title_bbox[3] - title_bbox[1]

        if title_w <= max_width and title_h <= available_title_height:
            best_font = font
            break

    if best_font is None:
        best_font = ImageFont.truetype(font_bold_path, 38)

    # ----------------------------
    # FINAL TITLE SIZE
    # ----------------------------
    title_bbox = draw.multiline_textbbox((0, 0), title, font=best_font, spacing=12)
    title_w = title_bbox[2] - title_bbox[0]
    title_h = title_bbox[3] - title_bbox[1]

    # ----------------------------
    # BOTTOM ANCHOR POSITIONING
    # ----------------------------
    current_y = HEIGHT - bottom_padding

    title_y = current_y - title_h
    title_x = (WIDTH - title_w) // 2

    cat_y = title_y - gap - box_h
    cat_x = (WIDTH - box_w) // 2

    # ----------------------------
    # HARD SAFETY CLAMP (NO OVERFLOW)
    # ----------------------------
    if title_y + title_h > HEIGHT - 20:
        title_y = HEIGHT - title_h - 20

    if title_y < HEIGHT * 0.60:
        title_y = int(HEIGHT * 0.60)
    
    SAFFRON = (255, 140, 0)     # softer saffron
    GREEN = (0, 120, 60)        # deeper green
    NAVY = (10, 40, 120)        # rich blue (for category)

    #draw strips
    strip_height = 20

    draw.rectangle(
        [0, 0, WIDTH, strip_height],
        fill=SAFFRON
    )

    draw.rectangle(
        [0, HEIGHT - strip_height, WIDTH, HEIGHT],
        fill=GREEN
    )

    # ----------------------------
    # DRAW CATEGORY BOX
    # ----------------------------
    draw.rounded_rectangle(
        [cat_x, cat_y, cat_x + box_w, cat_y + box_h],
        radius=25,
        fill=NAVY  
    )

    text_x = cat_x + (box_w - cat_text_w) // 2
    text_y = cat_y + (box_h - cat_text_h) // 2 - 2

    draw.text(
        (text_x, text_y),
        category_text,
        font=font_category,
        fill="white"
    )

    # ----------------------------
    # DRAW TITLE
    # ----------------------------
    draw.multiline_text(
        (title_x+3, title_y+3),
        title,
        font=best_font,
        fill="black",
        spacing=12,
        align="center"
    )

    draw.multiline_text(
        (title_x, title_y),
        title,
        font=best_font,
        fill="white",
        spacing=12,
        align="center"
    )

    # ----------------------------
    # SAVE IMAGE
    # ----------------------------
    output_path = "generated_posts/post.png"
    os.makedirs("generated_posts", exist_ok=True)

    bg.save(output_path)

    print("✅ IMAGE CREATED:", output_path)

    return output_path