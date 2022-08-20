from copy import deepcopy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

FONT_PATH = Path(__file__).parent / "chinese.stzhongs.ttf"
BACKGROUND_PATH = Path(__file__).parent / "background.jpg"

FONT_SIZE = 148
PADDING_TO_FONT_RATIO = 1 / 8 / 2
FONT = ImageFont.truetype(str(FONT_PATH), size=FONT_SIZE, layout_engine=ImageFont.LAYOUT_RAQM)
FILL = "white"
LANGUAGE = "zh"
BACKGROUND = Image.open(BACKGROUND_PATH)

PUNCTUATION_MARKS_WITH_WRONG_WIDTH = "，。、"


def ch_text_substitution(string: str) -> str:
    string = string.replace("\n", "")
    for punctuation_mark in PUNCTUATION_MARKS_WITH_WRONG_WIDTH:
        new_string = string.removesuffix(punctuation_mark)
        if new_string != string:
            return new_string + "."
    return string


class ToManyLinesError(Exception):
    ...


def get_preview(text: str) -> Image:
    image = deepcopy(BACKGROUND)
    draw = ImageDraw.Draw(image)

    if "\\n" in text:  # multiline text
        lines = text.split("\\n")
        if len(lines) != 2:
            raise ToManyLinesError("Text has to contains two lines or fewer")

        h_mid = image.size[1] / 2

        first_line = lines[0]
        w_1, h_1 = FONT.getsize(ch_text_substitution(first_line))
        x_1 = (image.size[0] - w_1) / 2
        y_1 = h_mid - h_1 * (1 + PADDING_TO_FONT_RATIO)
        draw.text((x_1, y_1), text=first_line, fill=FILL, font=FONT, language=LANGUAGE)

        second_line = lines[1]
        w_2, h_2 = FONT.getsize(ch_text_substitution(second_line))
        x_2 = (image.size[0] - w_2) / 2
        y_2 = h_mid + PADDING_TO_FONT_RATIO * h_2
        draw.text((x_2, y_2), text=second_line, fill=FILL, font=FONT, language=LANGUAGE)

    else:
        w, h = FONT.getsize(ch_text_substitution(text))
        x = (image.size[0] - w) / 2
        y = (image.size[1] - h) / 2
        draw.text((x, y), text=text, fill=FILL, font=FONT, language=LANGUAGE)

    return image
