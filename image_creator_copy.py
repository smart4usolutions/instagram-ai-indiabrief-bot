import os
import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

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
# RESIZE IMAGE
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
# TEXT WRAP (PIXEL BASED)
# ----------------------------
def wrap_text_by_pixels(draw, text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + " " + word if current_line else word

        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]

        if width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return "\n".join(lines)

def get_template_style(template):
    if template == "urgent":
        return {
            "bg": (75, 10, 10),
            "title_color": (255, 255, 255),
            "highlight_color": (220, 38, 38),
            "secondary" : (120, 120, 120),
            "tag": "BREAKING"
        }

    elif template == "growth":
        return {
            "bg": (10, 65, 10),
            "title_color": (230, 255, 240),
            "highlight_color": (34, 197, 94),
            "secondary" : (120, 140, 130),
            "tag": "MARKET"
        }

    elif template == "shocking":
        return {
            "bg": (100, 85, 20),
            "title_color": (255, 255, 255),
            "highlight_color": (255, 204, 0),
            "secondary" : (140, 140, 140),
            "tag": "SHOCKING"
        }

    else:  # explainer
        return {
            "bg": (10, 45, 90),
            "title_color": (230, 240, 255),
            "highlight_color": (96, 165, 250),
            "secondary" : (130, 150, 180),
            "tag": "EXPLAINED"
        }

# ----------------------------
# MAIN FUNCTION
# ----------------------------
# def create_post_image(title, image_url, category, discption, inset_url=None):
def create_post_image(title, image_url, category, description, template, inset_url=None):

    style = get_template_style(template)

    canvas = Image.new("RGB", (WIDTH, HEIGHT), style["bg"])
    draw = ImageDraw.Draw(canvas)

    # ---------------- IMAGE ----------------
    padding_x = 40   # reduced padding
    padding_top = 60

    img_width = WIDTH - (padding_x * 2)
    img_height = int(HEIGHT * 0.5)

    main_img = load_image(image_url)
    main_img = resize_cover(main_img, img_width, img_height)

    img_x = padding_x
    img_y = padding_top

    canvas.paste(main_img, (img_x, img_y))

    draw.rectangle(
        [img_x - 10, img_y - 10, img_x + img_width + 10, img_y + img_height + 10],
        outline="white",
        width=10
    )

    # ---------------- FONTS ----------------
    font_bold_path = os.path.join(BASE_DIR, "fonts/ARIALBD.TTF")
    font_regular_path = os.path.join(BASE_DIR, "fonts/ARIAL.TTF")

    #----------------- Template Style -----------

    # TAG
    tag_font = ImageFont.truetype(font_bold_path, 36)

    draw.rectangle([40, 40, 260, 90], fill=style["highlight_color"])

    draw.text((60, 50), style["tag"], font=tag_font, fill="black")


    # ---------------- CATEGORY ----------------
    cat_y = img_y + img_height + 20

    category_text = category.upper()
    font_category = ImageFont.truetype(font_bold_path, 38)

    bbox = draw.textbbox((0, 0), category_text, font=font_category)
    text_w = bbox[2] - bbox[0]

    draw.text(
        ((WIDTH - text_w) // 2, cat_y),
        category_text,
        font=font_category,
        fill=(255, 180, 0)
    )

    # ---------------- TEXT AREA ----------------
    top_y = cat_y + 60
    bottom_limit = HEIGHT - 140
    max_height = bottom_limit - top_y

    description = " ".join(description.split()[:30])  # limit length

    best = None

    for title_size in range(90, 40, -2):
        for desc_size in range(42, 22, -2):

            font_title = ImageFont.truetype(font_bold_path, title_size)
            font_desc = ImageFont.truetype(font_regular_path, desc_size)

            max_width = WIDTH - 80   # LESS SIDE PADDING

            wrapped_title = wrap_text_by_pixels(draw, title, font_title, max_width)
            wrapped_desc = wrap_text_by_pixels(draw, description, font_desc, max_width)

            title_bbox = draw.multiline_textbbox((0, 0), wrapped_title, font=font_title, spacing=8)
            desc_bbox = draw.multiline_textbbox((0, 0), wrapped_desc, font=font_desc, spacing=6)

            title_h = title_bbox[3] - title_bbox[1]
            desc_h = desc_bbox[3] - desc_bbox[1]

            gap = 40  # space between title & description
            total_h = title_h + gap + desc_h

            if total_h <= max_height:
                best = (font_title, font_desc, wrapped_title, wrapped_desc, title_h)
                break

        if best:
            break

    if not best:
        font_title = ImageFont.truetype(font_bold_path, 48)
        font_desc = ImageFont.truetype(font_regular_path, 26)
        wrapped_title = title
        wrapped_desc = description
        title_h = 120
    else:
        font_title, font_desc, wrapped_title, wrapped_desc, title_h = best

    # ---------------- DRAW CENTER ----------------
    def draw_center(text, y, font, color, spacing):
        bbox = draw.multiline_textbbox((0, 0), text, font=font, spacing=spacing)
        w = bbox[2] - bbox[0]
        x = (WIDTH - w) // 2

        draw.multiline_text(
            (x, y),
            text,
            font=font,
            fill=color,
            spacing=spacing,
            align="center"
        )

    # ---------------- DRAW TEXT ----------------
    draw_center(wrapped_title, top_y, font_title, style["title_color"], 8)

    draw_center(
        wrapped_desc,
        top_y + title_h + 40,
        font_desc,
        (220, 220, 220),
        6
    )

    # ---------------- FOOTER ----------------
    line_y = HEIGHT - 80

    draw.line(
        [(120, line_y), (WIDTH - 120, line_y)],
        fill=(80, 80, 80),
        width=3
    )

    font_footer = ImageFont.truetype(font_regular_path, 30)

    # Split text
    text1 = "Follow "
    text2 = "@ai.indiabrief"
    text3 = " for latest updates"

    # Measure each part
    bbox1 = draw.textbbox((0, 0), text1, font=font_footer)
    bbox2 = draw.textbbox((0, 0), text2, font=font_footer)
    bbox3 = draw.textbbox((0, 0), text3, font=font_footer)

    w1 = bbox1[2] - bbox1[0]
    w2 = bbox2[2] - bbox2[0]
    w3 = bbox3[2] - bbox3[0]

    total_w = w1 + w2 + w3

    # Start X (centered)
    start_x = (WIDTH - total_w) // 2
    y = line_y + 20

    # Draw each part
    draw.text((start_x, y), text1, font=font_footer, fill="white")

    draw.text((start_x + w1, y), text2, font=font_footer, fill=(255, 255, 0))  # Yellow

    draw.text((start_x + w1 + w2, y), text3, font=font_footer, fill="white")

    # ---------------- SAVE ----------------
    output_path = "generated_posts/post.png"
    os.makedirs("generated_posts", exist_ok=True)
    canvas.save(output_path)

    print("✅ IMAGE CREATED:", output_path)

    return output_path

#create_post_image("Renault's shocking plan to make India one of their top global markets by 2030", "https://bl-i.thgim.com/public/incoming/e4jjed/article70868662.ece/alternates/LANDSCAPE_1200/2026-04-14T170723Z_173063768_RC28ADA5NOMR_RTRMADP_3_RENAULT-JOBS.JPG", "India", "The company also wants India to rank among Renault's top three global markets by 2030, and aims ‌to capture about 5% of market share in the country by the end ‌of the decade","explainer")