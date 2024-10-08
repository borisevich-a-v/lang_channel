import json
from datetime import datetime
from typing import List

import gspread
from loguru import logger
from pydantic import BaseModel
from telegram import PhotoSize, Voice

from config import settings
from schemas import FinishedPost


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
        self.archive = self.spreadsheet.worksheet("archive")
        logger.info("Setup worksheet successfully")

    def save_post(self, post: FinishedPost, worksheet=None) -> None:
        if worksheet is None:
            worksheet = self.worksheet
        logger.info(f"Saving post {post.id_}")
        photo = json.dumps(
            {
                "file_id": post.photo.file_id,
                "file_unique_id": post.photo.file_unique_id,
                "width": post.photo.width,
                "height": post.photo.height,
                "file_size": post.photo.file_size,
            }
        )
        voice = json.dumps(
            {
                "duration": post.voice.duration,
                "mime_type": post.voice.mime_type,
                "file_id": post.voice.file_id,
                "file_size": post.voice.file_size,
                "file_unique_id": post.voice.file_unique_id,
            }
        )
        row_to_adding = [post.id_, post.text, photo, voice]
        response = worksheet.append_row(row_to_adding, include_values_in_response=True)
        # Add custom exp
        if not response:
            raise ValueError("The post was not saved")
        logger.info(f"Post {post.id_} was saved")

    def get_next_posts(self, amount) -> List[FinishedPost]:
        logger.info(f"Get {amount} posts")
        values = self.worksheet.get_values(f"A1:Z{amount}")
        posts = []
        for row in values:
            id_ = row[0]
            text = row[1]
            photo_dict = json.loads(row[2])
            photo = PhotoSize(**photo_dict)
            voice_dict = json.loads(row[3])
            voice = Voice(**voice_dict)
            post = FinishedPost(id_=id_, text=text, photo=photo, voice=voice)
            posts.append(post)
        return posts

    def get_next_post_and_move_it_to_archive(self) -> FinishedPost:
        post = self.get_next_posts(1)[0]
        self.save_post(post, worksheet=self.archive)
        self.worksheet.delete_rows(1)
        return post


registry = SpreadSheet()
