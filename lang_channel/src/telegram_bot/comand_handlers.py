import traceback
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from loguru import logger
from pydantic import BaseModel
from telegram import Update, User

from ..config import settings
from ..google_sheets import registry
from ..preview.get_preview import ToManyLinesError, get_preview
from ..schemas import FinishedPost, RawPost

PREVIEW_PATH = Path("../previews")
PREVIEW_PATH.mkdir(exist_ok=True)

user_response_yes = ("норм", "да", "yes", "是")
user_response_no = ("нет", "не совсем", "no", "не норм", "不是")


class Pipelines(Enum):
    CREATE_POST = "/create_post"
    NEXT_3_POSTS = "/get_3_next_posts"
    NEXT_10_POSTS = "/get_10_next_posts"


class Result(BaseModel):
    success: bool = True
    response_message: Optional[str]

    class Config:
        arbitrary_types_allowed = True


class RequestProcessingFlow:
    def __init__(self, *steps: Callable):
        self.steps = steps


class UserContext:
    def __init__(self, tg_user: User, post_registry):
        logger.info(f"Creating new user context for {tg_user.name} (id={tg_user.id})")
        self.id = tg_user.id
        self.tg_user = tg_user
        self.post_registry = post_registry

        self.steps = (
            self.check_user,
            self.get_3_last_posts,
            self.get_10_last_posts,
            self.create_post,
            self.receive_post_text,
            self.receive_audio,
            self.approve_post,
        )

        self.post = RawPost()
        self.last_step: Optional[Callable] = None
        self.preview_path: Optional[Path] = None

    async def process_reply(self, update: Update) -> Result:
        logger.info(f"Process {update.message.id} for {self.tg_user.name}")
        for step in self.steps:
            if result := await step(update):
                if result.success is True:
                    self.last_step = step
                    return result
                else:
                    self.last_step = None
                    return result
        response = "Хмм. Не могу понять. Попробуй исправить сообщение или начать по новой"
        return Result(success=False, response_message=response)

    async def check_user(self, update: Update):
        user_id = str(update.message.from_user.id)
        if user_id not in settings.allowed_users:
            return Result(success=False, response_message="401: contact bot admin pls")
        return None

    def _is_text_for_post(self, update: Update) -> bool:
        return update.message.text and len(update.message.text.split("\n")) == 4

    async def receive_post_text(self, update: Update):
        if self.last_step != self.create_post and not self._is_text_for_post(update):
            return None
        self.post = RawPost()
        try:
            ch_text, ru_text, transcription, hashtags = update.message.text.split("\n")
        except ValueError:
            return Result(success=False, response_message="Вроде бы вы отравили не четыре строки")
        try:
            preview = get_preview(ch_text)
            self.preview_path = PREVIEW_PATH / f"{self.id}.jpeg"
            preview.save(self.preview_path)
        except ToManyLinesError as exp:
            return Result(success=False, response_message=str(exp))
        except Exception:
            traceback.print_exc()
            return Result(success=False, response_message="Что-то не так с созданием превью")
        if not self.preview_path:
            raise ValueError()  # fix
        with open(self.preview_path, "rb") as fout:
            result = await self.tg_user.send_photo(photo=fout)
            self.post.photo = result.photo[0]
        ch_text = ch_text.replace("\\n", " ")
        ch_text = f"🇨🇳 {ch_text}"
        ru_text = f"🇷🇺 {ru_text}"
        transcription = f"🗣 {transcription}"
        self.post.text = "\n\n".join([ch_text, ru_text, transcription, hashtags])

        return Result(
            success=True,
            response_message="Запишите аудио",
        )

    async def receive_audio(self, update: Update) -> Optional[Result]:
        if self.last_step != self.receive_post_text or update.message.voice is None:
            return None
        result = await self._receive_audio(update)
        return result

    async def _receive_audio(self, update: Update) -> Optional[Result]:
        self.post.voice = update.message.voice

        if not self.preview_path:  # fix
            raise ValueError()
        with open(self.preview_path, "rb") as fout:
            await self.tg_user.send_photo(photo=fout, caption=self.post.text)
        await self.tg_user.send_voice(self.post.voice)
        return Result(
            success=True,
            response_message="Теперь проверь пост целиком и ответь норм/не норм",
        )

    async def approve_post(self, update: Update) -> Optional[Result]:
        if self.last_step not in (self.receive_audio, self.approve_post):
            return None

        if update.message.voice:
            result = await self._receive_audio(update)
            return result

        if update.message.text.lower() in user_response_yes:
            post_to_save = FinishedPost.parse_raw_post(self.post)
            registry.save_post(post_to_save)
            return Result(
                success=True,
                response_message="Отлично, пост сохранен в конец очереди",
            )
        if update.message.text.lower() in user_response_no:
            return Result(success=False, response_message="Тогда давай всё сначала")
        return None

    async def create_post(self, update: Update) -> Optional[Result]:
        command = update.message.text
        if command == Pipelines.CREATE_POST.value:
            response_message = (
                "Отправь четыре строки вот в таком формате:\n\nФраза на китайском.\nФраза на русском\nПиньинь\nХэштэги"
            )
            self.post = RawPost()
            return Result(response_message=response_message, pipeline=Pipelines.CREATE_POST)
        return None

    async def get_3_last_posts(self, update: Update) -> Optional[Result]:
        command = update.message.text
        if command == Pipelines.NEXT_3_POSTS.value:
            await self._send_n_last_posts(3)
            return Result(response_message=None, pipeline=Pipelines.NEXT_3_POSTS)
        return None

    async def get_10_last_posts(self, update: Update) -> Optional[Result]:
        command = update.message.text
        if command == Pipelines.NEXT_10_POSTS.value:
            await self._send_n_last_posts(10)
            return Result(response_message=None, pipeline=Pipelines.NEXT_3_POSTS)
        return None

    async def _send_n_last_posts(self, n: int) -> None:
        posts = registry.get_next_posts(amount=n)
        for i, post in enumerate(posts):
            await self.tg_user.send_message(text="=" * 10 + f"Пост {i + 1}:" + "=" * 10)
            await self.tg_user.send_photo(photo=post.photo, caption=post.text)
            await self.tg_user.send_voice(voice=post.voice)
