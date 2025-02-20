from copy import deepcopy
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


class PreviewError(Exception): ...


FONT_PATH = Path(__file__).parent / "chinese.stzhongs.ttf"
BACKGROUND_PATH = Path(__file__).parent / "background.jpg"

FONT_SIZE = 148
PADDING_TO_FONT_RATIO = 1 / 8 / 2  # font / 8 / sides_amount
FONT = ImageFont.truetype(str(FONT_PATH), size=FONT_SIZE, layout_engine=ImageFont.Layout.RAQM)
FILL = "#013220"  # Dark green
LANGUAGE = "zh"  # chinese
BACKGROUND = Image.open(BACKGROUND_PATH)
PUNCTUATION_MARKS_WITH_WRONG_WIDTH = "，。、"


def ch_text_substitution(string: str) -> str:
    string = string.replace("\n", "")
    for punctuation_mark in PUNCTUATION_MARKS_WITH_WRONG_WIDTH:
        new_string = string.removesuffix(punctuation_mark)
        if new_string != string:
            return new_string + "."
    return string


def get_text_size(text) -> tuple[float, float]:
    text_bbox = FONT.getbbox(ch_text_substitution(text))
    w = text_bbox[2] - text_bbox[0]
    h = text_bbox[3] - text_bbox[1]
    return w, h


def get_multiline_preview(text: str, image: Image, draw: ImageDraw.Draw) -> Image:
    lines = text.split("\\n")
    h_mid = image.size[1] / 2

    first_line = lines[0]
    w_1, h_1 = get_text_size(first_line)
    x_1 = (image.size[0] - w_1) / 2
    y_1 = h_mid - h_1 * (1 + PADDING_TO_FONT_RATIO)
    draw.text((x_1, y_1), text=first_line, fill=FILL, font=FONT, language=LANGUAGE)

    second_line = lines[1]
    w_2, h_2 = get_text_size(second_line)
    x_2 = (image.size[0] - w_2) / 2
    y_2 = h_mid + PADDING_TO_FONT_RATIO * h_2
    draw.text((x_2, y_2), text=second_line, fill=FILL, font=FONT, language=LANGUAGE)
    return image


def get_single_line_preview(text: str, image: Image, draw: ImageDraw.Draw) -> Image:
    w, h = get_text_size(text)
    x = (image.size[0] - w) / 2
    y = (image.size[1] - h) / 2
    draw.text((x, y), text=text, fill=FILL, font=FONT, language=LANGUAGE)
    return image


def get_preview(text: str) -> Image:
    if len(text.split("\\n")) > 2:
        raise PreviewError("Text has to contain two lines or fewer")

    image = deepcopy(BACKGROUND)
    draw = ImageDraw.Draw(image)
    if "\\n" in text:
        return get_multiline_preview(text, image, draw)
    else:
        return get_single_line_preview(text, image, draw)
