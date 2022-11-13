from typing import List

from loguru import logger
from src.commands.create_post_handler import CreatePostPipeline
from src.commands.get_next_post_handlers import GetNextPostPipeline
from src.commands.interfaces import IPipeline, Result
from src.commands.post_adding import PostAddingPipeline
from telegram import Update, User

from ..google_sheets import registry


class UserContext:
    def __init__(self, tg_user: User, post_registry):
        logger.info(f"Creating new user context for {tg_user.name} (id={tg_user.id})")
        self.id = tg_user.id
        self.tg_user = tg_user
        self.post_registry = post_registry

        self.pipelines: List[IPipeline] = [
            GetNextPostPipeline(self.tg_user, registry),
            PostAddingPipeline(self.tg_user),
            CreatePostPipeline(self.tg_user),
        ]

    async def process_reply(self, update: Update) -> Result:
        logger.info(f"Process {update.message.id} for {self.tg_user.name}")
        for pipeline in self.pipelines:
            result = await pipeline.handle_request(update)
            if result is not None:
                return result
        response = "Hmm, I didn't understood the message. Could you check it and send again?"
        return Result(success=False, response_message=response)
