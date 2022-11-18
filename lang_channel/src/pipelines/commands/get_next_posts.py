import re
from re import Pattern
from typing import Optional

from src.common import is_user_allowed
from src.google_sheets import SpreadSheet
from src.pipelines.commands.interfaces import ICommand
from src.pipelines.interfaces import Result
from telegram import Update, User


class GetNextPostsCommand(ICommand):
    COMMAND: Pattern = re.compile(r"\/get_(([1-2][0-9])|([1-9]))_next_posts")

    def __init__(self, user: User, post_repository: SpreadSheet):
        self.user = user
        self.post_repository = post_repository

    async def handle_request(self, update: Update) -> Optional[Result]:
        if not is_user_allowed(update):
            return Result(success=False, response_message="401: contact bot admin pls")
        if not self.is_update_processable(update):
            return None
        return await self.process_update(update)

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.user.username})>"

    async def process_update(self, update: Update) -> Result:
        post_amount = self.get_post_amount_from_command(update.message.text)
        posts = self.post_repository.get_next_posts(amount=post_amount)
        for i, post in enumerate(posts, start=1):
            await self.user.send_message(text="=" * 10 + f"Пост {i}:" + "=" * 10)
            await post.send_to_user(user=self.user)
        return Result(success=True)

    def get_post_amount_from_command(self, command):
        return command.lstrip("/get_").rstrip("_next_posts")

    @classmethod
    def is_update_processable(cls, update: Update) -> bool:
        if re.match(cls.COMMAND, update.message.text) is None:
            return False
        return True
