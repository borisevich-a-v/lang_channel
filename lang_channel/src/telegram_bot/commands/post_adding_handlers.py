from pathlib import Path
from typing import Optional

from src.google_sheets import registry
from src.preview.get_preview import get_preview
from src.schemas import FinishedPost
from src.telegram_bot.commands.common import NO_RESPONSE, YES_RESPONSE, HumanReadableException, Result
from src.validators.hashtags import validate_hashtags
from telegram import Update

PREVIEWS_DIRECTORY = Path("../previews")
PREVIEWS_DIRECTORY.mkdir(exist_ok=True)

APPROVE_QUERY_MESSAGE = "Check post and approve (да/yes) or disapprove (нет/no) post"


class PostTextHandler(PostHandler):
    async def execute(self, update: Update):
        try:
            await self.receive_post_text(update)
            return Result(success=True, response_message="Record audio please", post=self.post)
        except Exception as exp:
            return Result(success=False, response_message=str(exp))

    @classmethod
    def is_update_processable(cls, update: Update) -> bool:
        if not cls._is_text_for_post(update):
            return False

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
    def is_update_processable(cls, update: Update) -> bool:
        if update.message.voice is None:
            return False

    async def execute(self, update: Update):
        try:
            await self.receive_audio(update)
            return Result(success=True, response_message=APPROVE_QUERY_MESSAGE, post=self.post)
        except Exception as exp:
            return Result(success=False, response_message=str(exp))

    async def receive_audio(self, update: Update):
        self.post.voice = update.message.voice
        if not self.post.photo:
            raise HumanReadableException("Looks like photo of post is not saved. Try again please")
        await self.post.send_to_user(self.user)


class PostApproveAndSaveHandler(PostHandler):
    @classmethod
    def is_update_processable(cls, update: Update) -> bool:
        return True

    async def execute(self, update: Update):
        try:
            result = await self.approve_post(update)
            return result
        except Exception as exp:
            return Result(success=False, response_message=str(exp))

    async def approve_post(self, update: Update) -> Optional[Result]:
        if update.message.text.lower() in YES_RESPONSE:
            post_to_save = FinishedPost.parse_raw_post(self.post)
            registry.save_post(post_to_save)
            return Result(
                success=True,
                response_message="Great, post was saved in the tail of the queue",
            )
        elif update.message.text.lower() in NO_RESPONSE:
            return Result(success=False, response_message="Let's create post again")
        else:
            return Result(success=False, response_message=APPROVE_QUERY_MESSAGE)
