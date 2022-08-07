from copy import deepcopy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).parent / "chinese.stzhongs.ttf"
BACKGROUND_PATH = Path(__file__).parent / "background.jpg"

FONT = ImageFont.truetype(str(FONT_PATH), size=148, layout_engine=ImageFont.LAYOUT_RAQM)
FILL = "white"
BACKGROUND = Image.open(BACKGROUND_PATH)

punctuation_marks_with_additional_space = "，。、"


def ch_text_substitution(string: str) -> str:
    for punctuation_mark in punctuation_marks_with_additional_space:
        new_string = string.removesuffix(punctuation_mark)
        if new_string != string:
            return new_string + "."
    return string


def get_preview(text: str) -> Image:
    image = deepcopy(BACKGROUND)
    draw = ImageDraw.Draw(image)
    w, h = FONT.getsize(text)
    x = (image.size[0] - w) / 2
    y = (image.size[1] - h) / 2
    draw.text((x, y), text=text, fill=FILL, font=FONT, language="zh")
    return image
