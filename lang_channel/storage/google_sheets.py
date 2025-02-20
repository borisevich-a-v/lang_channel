import json
from typing import List

import gspread
from gspread import Worksheet
from loguru import logger
from telegram import PhotoSize, Voice

from lang_channel import config
from lang_channel.models import Post


class SpreadSheet:
    # No transactions is a problem. Consider to use some serverless solutions or maybe some libs for spreadsheets.
    def __init__(self) -> None:
        logger.info("Setting up worksheets...")
        self.spreadsheet = gspread.service_account().open(config.SPREADSHEET_NAME)

        self.new_posts_ws = self.spreadsheet.worksheet(config.NEW_POSTS_TABLE_NAME)
        self.archive_ws = self.spreadsheet.worksheet(config.ARCHIVE_TABLE_NAME)

    def save_new_post(self, post: Post) -> None:
        self._save_post(post, self.new_posts_ws)

    def _save_post(self, post: Post, worksheet: Worksheet) -> None:
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
        row_to_add = [post.id_, post.text, photo, voice, post.publish_count]
        response = worksheet.append_row(row_to_add, include_values_in_response=True)
        if not response:
            raise ValueError("The post was not saved")
        logger.info(f"Post {post.id_} was saved")

    def archive_post(self, control_post: Post) -> Post:
        """Only the first post can be archived. `control_post` is required for validation purposes only"""
        post = self.get_next_posts(1)[0]
        if post.id_ != control_post.id_:
            raise ValueError("Only the first post in the table can be archived!")

        self._save_post(post, worksheet=self.archive_ws)
        self.new_posts_ws.delete_rows(1)
        return post

    def get_next_posts(self, amount: int) -> List[Post]:
        logger.info(f"Get {amount} posts")
        values = self.new_posts_ws.get_values(f"A1:Z{amount}")
        posts = []
        for row in values:
            if not row:
                continue
            id_ = row[0]

            text = row[1]

            photo_dict = json.loads(row[2])
            photo = PhotoSize(**photo_dict)

            voice_dict = json.loads(row[3])
            voice = Voice(**voice_dict)

            publish_count = row[4]

            post = Post(id_=id_, text=text, photo=photo, voice=voice, publish_count=publish_count)
            posts.append(post)

        return posts


registry = SpreadSheet()
