from typing import Optional

from src.telegram_bot.commands.common import Result, is_user_allowed
from telegram import Update, User


class CreatePostContext:
    def __init__(self, user: User):
        self.user = user

    COMMAND = "/create_post"

    async def handle_request(self, update: Update) -> Optional[Result]:
        if not is_user_allowed(update):
            return Result(success=False, response_message="401: contact bot admin pls")
        command = update.message.text
        if command == "/create_post":
            response_message = (
                "Отправь четыре строки вот в таком формате:\n\nФраза на китайском.\nФраза на русском\nПиньинь\nХэштэги"
            )
            return Result(response_message=response_message, success=True)
        return None
