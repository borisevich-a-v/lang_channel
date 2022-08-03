import json
import logging
from datetime import date, datetime
from typing import List

import gspread
from pydantic import BaseModel
from telegram import PhotoSize, Voice

from post_creator_bot.src.config import settings
from post_creator_bot.src.schemas import Post

logger = logging.getLogger(__file__)


class Row(BaseModel):
    word: str
    added_at: datetime
    priority: int


class Table(BaseModel):
    rows: List[Row]


class SpreadSheet:
    type = "spreadsheet"

    def __init__(self) -> None:
        self.gc = gspread.service_account()
        self.spreadsheet = self.gc.open(settings.spreadsheet_name)
        self.worksheet = self.spreadsheet.worksheet("posts")
        self.metadata = self.spreadsheet.worksheet("metadata")
        logger.info("Setup worksheet successfully")

    def save_post(self, post: Post) -> None:
        text, photo, voice = post.text, post.photo, post.voice
        logger.info(f"Saving {text=}")
        photo = json.dumps(
            {
                "file_id": photo.file_id,
                "file_unique_id": photo.file_unique_id,
                "width": photo.width,
                "height": photo.height,
                "file_size": photo.file_size,
            }
        )
        voice = json.dumps(
            {
                "duration": voice.duration,
                "mime_type": voice.mime_type,
                "file_id": voice.file_id,
                "file_size": voice.file_size,
                "file_unique_id": voice.file_unique_id,
            }
        )
        row_to_adding = [text, photo, voice]
        response = self.worksheet.append_row(
            row_to_adding, include_values_in_response=True
        )
        # Add custom exp
        if not response:
            raise ValueError("The post is not saved")
        logger.info(f"{text=} saved")

    def get_next_posts(self, amount) -> List[Post]:
        values = self.worksheet.get_values(f"A1:C{amount}")
        posts = []
        for row in values:
            text = row[0]
            photo_dict = json.loads(row[1])
            photo = PhotoSize(**photo_dict)
            voice_dict = json.loads(row[2])
            voice = Voice(**voice_dict)

            posts.append(Post(text=text, photo=photo, voice=voice))
        return posts


registry = SpreadSheet()
# registry.get_next_posts()

# photo = PhotoSize(width=90,
#                   height=51,
#                   file_id='AgACAgIAAxkDAAIBC2LoGj15e4g2Yz-51PQySvCPSr8KAAK6vDEbZZtBSw6t_i8DlzLTAQADAgADcwADKQQ',
#                   file_size=811,
#                   file_unique_id='AQADurwxG2WbQUt4')
#
# voice = Voice(
#     **{'duration': 1, 'mime_type': 'audio/ogg',
#        'file_id': 'AwACAgIAAxkBAAIBKGLoHDivKGej1f9VIv78VWuPbpzVAALsHgACZZtBS7JadnL2ZtdgKQQ', 'file_size': 5489,
#        'file_unique_id': 'AgAD7B4AAmWbQUs'}
# )
# registry.save_post(text="к\nh\nch", photo=photo, voice=voice)
