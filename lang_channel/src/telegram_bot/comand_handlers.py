from loguru import logger
from telegram import Update, User

from ..google_sheets import registry
from .commands.common import Result
from .commands.get_next_post_handlers import GetNextPostContext
from .commands.post_adding import PostAddingContext


class UserContext:
    def __init__(self, tg_user: User, post_registry):
        logger.info(f"Creating new user context for {tg_user.name} (id={tg_user.id})")
        self.id = tg_user.id
        self.tg_user = tg_user
        self.post_registry = post_registry

        self.pipelines = (
            GetNextPostContext(self.tg_user, registry),
            PostAddingContext(self.tg_user),
        )

    async def process_reply(self, update: Update) -> Result:
        logger.info(f"Process {update.message.id} for {self.tg_user.name}")
        for pipeline in self.pipelines:
            result = await pipeline.handle_request(update)
            if result:
                return result
        response = "Hmm, I didn't understood the message. Could you check it and send again?"
        return Result(success=False, response_message=response)

    #
    # async def create_post(self, update: Update) -> Optional[Result]:
    # "/create_post"
    #     command = update.message.text
    #     if command == Pipelines.CREATE_POST.value:
    #         response_message = (
    #            "Отправь четыре строки вот в таком формате:\n\nФраза на китайском.\nФраза на русском\nПиньинь\nХэштэги"
    #         )
    #         self.post = RawPost()
    #         return Result(response_message=response_message, pipeline=Pipelines.CREATE_POST)
    #     return None
