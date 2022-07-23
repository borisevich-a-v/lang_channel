from copy import deepcopy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).parent / "chinese.stzhongs.ttf"
BACKGROUND_PATH = Path(__file__).parent / "background.jpg"

FONT = ImageFont.truetype(str(FONT_PATH), size=148)
FILL = "white"
BACKGROUND = Image.open(BACKGROUND_PATH)


def get_preview(text: str) -> Image:
    background = deepcopy(BACKGROUND)
    draw = ImageDraw.Draw(background)
    w, h = draw.textsize(text, language="zh", font=FONT)
    x = (background.size[0] - w) / 2
    y = (background.size[1] - h) / 2
    draw.text((x, y), text=text, fill=FILL, font=FONT, language="zh")
    return background
