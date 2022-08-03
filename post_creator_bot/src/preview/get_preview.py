from copy import deepcopy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).parent / "chinese.stzhongs.ttf"
BACKGROUND_PATH = Path(__file__).parent / "background.jpg"

FONT = ImageFont.truetype(str(FONT_PATH), size=148)
FILL = "white"
BACKGROUND = Image.open(BACKGROUND_PATH)

chinese_punctuation_marks = "，。、"  # rename


def ch_text_substitution(string: str) -> str:
    for punctuation_mark in chinese_punctuation_marks:
        new_string = string.removesuffix(punctuation_mark)
        if new_string != string:
            return new_string + "."
    return string


def get_preview(text: str) -> Image:
    image = deepcopy(BACKGROUND)
    draw = ImageDraw.Draw(image)
    w, h = draw.textsize(ch_text_substitution(text), language="zh", font=FONT)
    x = (image.size[0] - w) / 2
    y = (image.size[1] - h) / 2
    draw.text((x, y), text=text, fill=FILL, font=FONT, language="zh")
    return image
