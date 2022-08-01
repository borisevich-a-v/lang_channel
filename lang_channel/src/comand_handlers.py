from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from pydantic import BaseModel
from telegram import PhotoSize, Update
from telegram import User as TelegramUser
from telegram import Voice

from lang_channel.src.google_sheets import registry
from lang_channel.src.preview.get_preview import get_preview

PREVIEW_PATH = Path("../previews")
PREVIEW_PATH.mkdir(exist_ok=True)


class Pipelines(Enum):
    CREATE_POST = "/create_post"
    NEXT_3_POSTS = "/get_3_next_posts"


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
            self.parse_command,
            self.create_post,
            self.approve_picture_and_text,
            self.get_audio,
            self.approve_post,
        )
        self.post_registry = post_registry

        self.text: Optional[str] = None
        self.photo: Optional[PhotoSize] = None
        self.voice: Optional[Voice] = None
        self.last_step: Optional[Callable] = None
        self.preview_path: Optional[Path] = None

    async def create_post(self, update: Update):
        if self.last_step != self.parse_command:
            return None
        try:
            ch_text, ru_text, transcription = update.message.text.split("\n")
        except ValueError:
            return Result(
                success=False, response_message="Вроде бы вы отравили не три строки"
            )
        self.text = "\n".join([ch_text, ru_text, transcription])
        try:
            preview = get_preview(ch_text)
            self.preview_path = PREVIEW_PATH / f"{ch_text}.jpeg"
            preview.save(self.preview_path)
        except:
            return Result(
                success=False, response_message="Что-то не так с созданием превью"
            )

        if not self.preview_path:
            raise ValueError()  # fix
        with open(self.preview_path, "rb") as fout:
            result = await self.tg_user.send_photo(photo=fout, caption=self.text)
            self.photo = result.photo[0]
            print(self.photo)
        return Result(
            success=True,
            response_message="Проверьте, что всё в порядке и ответьте да/нет",
        )

    async def process_reply(self, update: Update) -> Result:
        response = "Хмм. Не могу понять. Попробуй начать по новой"
        for step in self.steps:
            if result := await step(update):
                if result.success is True:
                    self.last_step = step
                    return result
                else:
                    self.last_step = None
                    return result
        return Result(success=False, response_message=response)

    async def approve_picture_and_text(self, update: Update):
        if self.last_step != self.create_post:
            return None
        if update.message.text.lower() in ("норм", "да", "yes", "是"):
            return Result(success=True, response_message="Отлично, запишите аудио")
        if update.message.text.lower() in ("нет", "не совсем", "no", "не норм", "不是"):
            return Result(success=False, response_message="Тогда давай всё сначала")

    async def get_audio(self, update: Update):
        if self.last_step != self.approve_picture_and_text:
            return None
        self.voice = update.message.voice
        if not self.preview_path:  # fix
            raise ValueError()
        with open(self.preview_path, "rb") as fout:
            await self.tg_user.send_photo(photo=fout, caption=self.text)
        await self.tg_user.send_voice(self.voice)
        print(self.voice)
        return Result(
            success=True,
            response_message="Теперь проверь пост целиком и ответь норм/не норм",
        )

    async def approve_post(self, update: Update):
        if self.last_step != self.get_audio:
            return None
        if update.message.text.lower() in ("норм", "да", "yes", "是"):
            return Result(
                success=True,
                response_message="Отлично, надо дописать код и можно запускать канал",
            )
        if update.message.text.lower() in ("нет", "не совсем", "no", "не норм", "不是"):
            return Result(success=False, response_message="Тогда давай всё сначала")

    async def parse_command(self, update: Update) -> Optional[Result]:
        command = update.message.text
        if command == Pipelines.CREATE_POST.value:
            response_message = "Отправь три строки вот в таком формате:\n\nФраза на китайском.\nФраза на русском\nПиньинь"
            return Result(
                response_message=response_message, pipeline=Pipelines.CREATE_POST
            )
        elif command == Pipelines.NEXT_3_POSTS.value:
            await self.tg_user.send_message(text="Пост 1")
            text, photo, voice = registry.get_post()
            await self.tg_user.send_photo(photo=photo, caption=text)
            await self.tg_user.send_voice(voice=voice)
            return Result(response_message=None, pipeline=Pipelines.NEXT_3_POSTS)

        return None
