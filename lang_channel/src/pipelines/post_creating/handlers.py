import traceback
from abc import ABC
from pathlib import Path
from typing import Optional

from src.common import HumanReadableException, Result
from src.google_sheets import registry
from src.pipelines.interfaces import IHandler
from src.preview.get_preview import get_preview
from src.schemas import FinishedPost, RawPost
from src.validators.hashtags import validate_hashtags
from telegram import Update, User, InlineKeyboardButton, InlineKeyboardMarkup

PREVIEWS_DIRECTORY = Path("../previews")
PREVIEWS_DIRECTORY.mkdir(exist_ok=True)

APPROVE, DISAPPROVE = "да", "нет"


class PostHandler(IHandler, ABC):
    BUTTONS = [[InlineKeyboardButton("👍", callback_data=APPROVE), InlineKeyboardButton("👎", callback_data=DISAPPROVE)]]

    def __init__(self, user: User, post: RawPost):
        self.user = user
        self.post = post

    async def send_message_to_user(self) -> None:
        if not self.post.text and not self.post.voice:
            await self.user.send_message("Send text and record audio for post.")
        elif not self.post.text and self.post.voice:
            await self.user.send_message("Send text for post.")
        elif self.post.text and not self.post.voice:
            await self.user.send_message("Record audio for post please.")
        else:
            await self.post.send_to_user(self.user)
            await self.user.send_message("Great, check post and approve or disapprove post")
                                         # reply_markup=InlineKeyboardMarkup(self.BUTTONS))


class PostTextHandler(PostHandler):
    async def execute(self, update: Update) -> Result:
        try:
            await self.receive_post_text(update)
            await self.send_message_to_user()
            return Result(success=True)
        except Exception as exp:
            traceback.print_exc()
            return Result(success=False, response_message=str(exp))

    @classmethod
    def is_update_processable(cls, update: Update, *args, **kwargs) -> bool:
        if not cls._is_text_for_post(update):
            return False
        return True

    @staticmethod
    def _is_text_for_post(update: Update) -> bool:
        return update.message.text and len(update.message.text.split("\n")) == 4

    def create_and_save_preview(self, text) -> Path:
        preview = get_preview(text)
        preview_path = PREVIEWS_DIRECTORY / f"{self.user.id}.jpeg"
        preview.save(preview_path)
        return preview_path

    def replace_empty_hashtag_line(self, hashtags: str) -> str:
        if hashtags.strip() == "#":
            return ""
        return hashtags

    async def receive_post_text(self, update: Update):
        try:
            ch_text, ru_text, transcription, hashtags = update.message.text.split("\n")
        except ValueError:
            raise HumanReadableException("Unfortunately you have to send exactly 4 lines")

        hashtags = self.replace_empty_hashtag_line(hashtags)
        validate_hashtags(hashtags)

        preview_path = self.create_and_save_preview(ch_text)
        with open(preview_path, "rb") as fout:
            photo = await self.user.send_photo(photo=fout)
            self.post.photo = photo.photo[0]

        ch_text = ch_text.replace("\\n", " ")
        ch_text = f"🇨🇳 {ch_text}"
        ru_text = f"🇷🇺 {ru_text}"
        transcription = f"🗣 {transcription}"

        self.post.text = "\n\n".join([ch_text, ru_text, transcription, hashtags])


class PostAudioHandler(PostHandler):
    @classmethod
    def is_update_processable(cls, update: Update, *args, **kwargs) -> bool:
        if update.message.voice is None:
            return False
        return True

    async def execute(self, update: Update):
        try:
            await self.receive_audio(update)
            await self.send_message_to_user()
            return Result(success=True)
        except Exception as exp:
            traceback.print_exc()
            return Result(success=False, response_message=str(exp))

    async def receive_audio(self, update: Update):
        self.post.voice = update.message.voice
        if not self.post.photo:
            raise HumanReadableException("Looks like photo of post is not saved. Try again please")


class PostApproveAndSaveHandler(PostHandler):
    @classmethod
    def is_update_processable(cls, update: Update, *args, **kwargs) -> bool:  # TODO: dix args
        if update.message.text in (APPROVE, DISAPPROVE):
            return True
        return False

    async def execute(self, update: Update):
        try:
            result = await self.approve_post(update)
            return result
        except Exception as exp:
            traceback.print_exc()
            return Result(success=False, response_message=str(exp))

    async def approve_post(self, update: Update) -> Optional[Result]:
        if update.message.text.lower() == APPROVE:
            post_to_save = FinishedPost.parse_raw_post(self.post)
            registry.save_post(post_to_save)
            self.post = RawPost()
            return Result(
                success=True,
                response_message="Great, post was saved in the tail of the queue",
            )
        elif update.message.text.lower() == DISAPPROVE:
            return Result(success=False, response_message="You can change text or audio")
        else:
            await self.send_message_to_user()
            return Result(success=False)
