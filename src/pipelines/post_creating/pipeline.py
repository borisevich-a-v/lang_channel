from typing import Optional

from telegram import Update, User

from common import Result, is_user_allowed
from pipelines import IPipeline
from pipelines.post_creating.handlers import PostApproveAndSaveHandler, PostAudioHandler, PostTextHandler
from schemas import RawPost


class PostAddingPipeline(IPipeline):
    HANDLERS = (
        PostTextHandler,
        PostAudioHandler,
        PostApproveAndSaveHandler,
    )

    def __init__(self, user: User):
        self.user = user
        self.post = RawPost()
        self._next_step_number: int = 0

    async def handle_request(self, update: Update) -> Optional[Result]:
        if not is_user_allowed(update):
            return Result(success=False, response_message="401: contact bot admin pls")

        step = None
        for handler in self.HANDLERS:
            if handler.is_update_processable(update):
                step = handler(self.user, self.post)
                break
        if not step:
            return None
        result = await step.execute(update)
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.user.username})>"
