from typing import cast

from telegram import Chat, Update


def get_chat_id(update: Update) -> int:
    return cast(Chat, update.effective_chat).id
