from typing import Optional

from telegram import Update, User

from lang_channel.common import Result, is_user_allowed
from lang_channel.pipelines.commands import ICommand


class CreatePostCommand(ICommand):
    """Send how to create post instruction to user"""

    COMMAND: str = "/create_post"

    def __init__(self, user: User):
        self.user = user

    async def handle_request(self, update: Update) -> Optional[Result]:
        if not is_user_allowed(update):
            return Result(success=False, response_message="401: contact bot admin pls")
        command = update.message.text
        if command == "/create_post":
            response_message = (
                "Отправь четыре строки вот в таком формате:\n\n"
                "Фраза на китайском.\nФраза на русском\nПиньинь\nХэштэги"
            )
            return Result(response_message=response_message, success=True)
        return None
