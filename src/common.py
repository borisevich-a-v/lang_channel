from typing import Optional

from pydantic import BaseModel
from telegram import Update

from config import settings
from schemas import RawPost


class HumanReadableException(Exception):
    pass


class Result(BaseModel):
    success: bool = True
    response_message: Optional[str] = None
    post: Optional[RawPost] = None

    class Config:
        arbitrary_types_allowed = True


def is_user_allowed(update: Update) -> bool:
    user_id = str(update.effective_user.id)
    if user_id not in settings.allowed_users:
        return False
    return True
