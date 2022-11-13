from typing import Optional

from src.commands.interfaces import IHandler, IPipeline, Result
from src.common import is_user_allowed
from src.google_sheets import SpreadSheet
from telegram import Update, User


class GetNextPostHandler(IHandler):
    COMMAND: str
    POST_AMOUNT: int

    def __init__(self, user: User, post_repository: SpreadSheet):
        self.user = user
        self.post_repository = post_repository

    async def execute(self, update: Update) -> Result:
        posts = self.post_repository.get_next_posts(amount=self.POST_AMOUNT)
        for i, post in enumerate(posts):
            await self.user.send_message(text="=" * 10 + f"Пост {i + 1}:" + "=" * 10)
            await post.send_to_user(user=self.user)
        return Result(success=True)

    @classmethod
    def is_update_processable(cls, update: Update) -> bool:
        if update.message.text == cls.COMMAND:
            return True
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}({self.POST_AMOUNT=}, {self.user=})"


class GetNext3PostsHandler(GetNextPostHandler):
    COMMAND = "/get_3_next_posts"
    POST_AMOUNT = 3


class GetNext10PostsHandler(GetNextPostHandler):
    COMMAND = "/get_10_next_posts"
    POST_AMOUNT = 10


class GetNext21PostsHandler(GetNextPostHandler):
    COMMAND = "/get_21_next_posts"
    POST_AMOUNT = 21


class GetNextPostPipeline(IPipeline):
    HANDLERS = (
        GetNext3PostsHandler,
        GetNext10PostsHandler,
        GetNext21PostsHandler,
    )

    def __init__(self, user: User, post_repository: SpreadSheet):
        self.user = user
        self.post_repository = post_repository

    async def handle_request(self, update: Update) -> Optional[Result]:
        if not is_user_allowed(update):
            return Result(success=False, response_message="401: contact bot admin pls")
        result = None
        for option in self.HANDLERS:
            if option.is_update_processable(update):
                result = await option(self.user, self.post_repository).execute(update)
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.user.username})>"
