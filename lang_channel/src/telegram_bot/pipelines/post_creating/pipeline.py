from typing import Optional

from telegram import User, Update

from src.common import Result, is_user_allowed
from src.schemas import RawPost
from src.telegram_bot.pipelines.interfaces import IPipeline
from src.telegram_bot.pipelines.post_creating.handlers import PostTextHandler, PostAudioHandler, \
    PostApproveAndSaveHandler


class PostAddingPipeline(IPipeline):
    STEPS_ORDER = (
        PostTextHandler,
        PostAudioHandler,
        PostApproveAndSaveHandler,
    )

    def __init__(self, user: User):
        self.user = user
        self.post = RawPost()
        self._next_step_number: int = 0

    @property
    def next_step(self) -> PostTextHandler:
        return self.STEPS_ORDER[self._next_step_number]

    def get_next_step_number(self):
        self._next_step_number += 1
        if self._next_step_number + 1 > len(self.STEPS_ORDER):
            self._next_step_number = 0

    async def handle_request(self, update: Update) -> Optional[Result]:
        if not is_user_allowed(update):
            return Result(success=False, response_message="401: contact bot admin pls")

        if not self.next_step.is_update_processable(update):
            return None

        next_step = self.next_step(self.user, self.post)
        result = await next_step.execute(update)
        if result.success:
            self.get_next_step_number()
        return result

    def __repr__(self):
        return f"<{self.__class__.__name__}({self.user.username})>"
