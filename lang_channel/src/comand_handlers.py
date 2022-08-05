import traceback
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from pydantic import BaseModel
from telegram import PhotoSize, Update
from telegram import User as TelegramUser
from telegram import Voice

from .google_sheets import registry
from .preview.get_preview import get_preview
from .schemas import Post

PREVIEW_PATH = Path("../previews")
PREVIEW_PATH.mkdir(exist_ok=True)


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


class User(TelegramUser):
    def __init__(self, tg_user: TelegramUser, post_registry):
        self.id = tg_user.id
        self.tg_user = tg_user
        self.steps = (
            self.begin_post_creating,
            self.get_3_last_posts,
            self.get_10_last_posts,
            self.create_post,
            self.get_audio,
            self.approve_post,
        )
        self.post_registry = post_registry

        self.text: Optional[str] = None
        self.photo: Optional[PhotoSize] = None
        self.voice: Optional[Voice] = None
        self.last_step: Optional[Callable] = None
        self.preview_path: Optional[Path] = None

    def clear_post(self):
        # TODO create post class
        self.voice, self.text, self.photo = None, None, None

    async def process_reply(self, update: Update) -> Result:
        for step in self.steps:
            if result := await step(update):
                if result.success is True:
                    self.last_step = step
                    return result
                else:
                    self.last_step = None
                    return result
        response = "Хмм. Не могу понять. Попробуй начать по новой"
        return Result(success=False, response_message=response)

    async def create_post(self, update: Update):
        if self.last_step != self.begin_post_creating:
            return None
        try:
            ch_text, ru_text, transcription, hashtags = update.message.text.split("\n")

        except ValueError:
            return Result(
                success=False, response_message="Вроде бы вы отравили не четыре строки"
            )
        try:
            preview = get_preview(ch_text)
            self.preview_path = PREVIEW_PATH / f"{self.id}.jpeg"
            preview.save(self.preview_path)
        except Exception:
            traceback.print_exc()
            return Result(
                success=False, response_message="Что-то не так с созданием превью"
            )
        if not self.preview_path:
            raise ValueError()  # fix
        with open(self.preview_path, "rb") as fout:
            result = await self.tg_user.send_photo(photo=fout, caption=self.text)
            self.photo = result.photo[0]
        ch_text = f"🇨🇳 {ch_text}"
        ru_text = f"🇷🇺 {ru_text}"
        transcription = f"🗣 {transcription}"
        self.text = "\n\n".join([ch_text, ru_text, transcription, hashtags])

        return Result(
            success=True,
            response_message="Запишите аудио",
        )

    async def get_audio(self, update: Update):
        if self.last_step != self.create_post:
            return None

        self.voice = update.message.voice
        if self.voice is None:
            return None

        if not self.preview_path:  # fix
            raise ValueError()
        with open(self.preview_path, "rb") as fout:
            await self.tg_user.send_photo(photo=fout, caption=self.text)
        await self.tg_user.send_voice(self.voice)
        return Result(
            success=True,
            response_message="Теперь проверь пост целиком и ответь норм/не норм",
        )

    async def approve_post(self, update: Update):
        if self.last_step != self.get_audio:
            return None
        if update.message.text.lower() in ("норм", "да", "yes", "是"):
            post_to_save = Post(text=self.text, photo=self.photo, voice=self.voice)
            registry.save_post(post_to_save)
            return Result(
                success=True,
                response_message="Отлично, пост сохранен в конец очереди",
            )
        if update.message.text.lower() in ("нет", "не совсем", "no", "не норм", "不是"):
            return Result(success=False, response_message="Тогда давай всё сначала")

    async def begin_post_creating(self, update: Update) -> Optional[Result]:
        command = update.message.text
        if command == Pipelines.CREATE_POST.value:
            response_message = "Отправь четыре строки вот в таком формате:\n\nФраза на китайском.\nФраза на русском\nПиньинь\nХэштэги"
            self.clear_post()
            return Result(
                response_message=response_message, pipeline=Pipelines.CREATE_POST
            )
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
