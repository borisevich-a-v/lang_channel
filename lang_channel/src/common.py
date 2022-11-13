from typing import Optional

from pydantic import BaseModel
from src.config import settings
from src.schemas import RawPost
from telegram import Update


class HumanReadableException(Exception):
    ...


YES_RESPONSE = (
    "норм",
    "да",
    "yes",
    "是",
)
NO_RESPONSE = (
    "нет",
    "не совсем",
    "no",
    "не норм",
    "不是",
)


class Result(BaseModel):
    success: bool = True
    response_message: Optional[str]
    post: Optional[RawPost]

    class Config:
        arbitrary_types_allowed = True


def is_user_allowed(update: Update) -> bool:
    user_id = str(update.message.from_user.id)
    if user_id not in settings.allowed_users:
        return False
    return True
