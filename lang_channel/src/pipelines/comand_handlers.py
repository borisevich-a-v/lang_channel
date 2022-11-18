from typing import List

from loguru import logger
from src.common import Result
from src.google_sheets import registry
from src.pipelines.commands.create_post_instruction import CreatePostCommand
from src.pipelines.commands.get_next_posts import GetNextPostsCommand
from src.pipelines.interfaces import IPipeline
from src.pipelines.post_creating.pipeline import PostAddingPipeline
from telegram import Update, User


class UserContext:
    def __init__(self, tg_user: User, post_registry):
        logger.info(f"Creating new user context for {tg_user.name} (id={tg_user.id})")
        self.id = tg_user.id
        self.tg_user = tg_user
        self.post_registry = post_registry

        self.pipelines: List[IPipeline] = [
            GetNextPostsCommand(self.tg_user, registry),
            PostAddingPipeline(self.tg_user),
            CreatePostCommand(self.tg_user),
        ]

    async def process_reply(self, update: Update) -> Result:
        logger.info(f"Process {update.message.id} for {self.tg_user.name}")
        for pipeline in self.pipelines:
            result = await pipeline.handle_request(update)
            if result is not None:
                return result
        response = "Hmm, I didn't understood the message. Could you check it and send again?"
        return Result(success=False, response_message=response)
