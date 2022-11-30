import asyncio
from typing import List

from loguru import logger
from telegram.ext import ApplicationBuilder, MessageHandler, Application, filters

from src.config import settings
from src.google_sheets import registry
from src.pipelines.comand_handler import UserContext
from telegram import Update, User


class LangBot:
    """
    Just wrapper to support legacy code
    It was designed for a few users
    """

    def __init__(self):
        self.user_contexts: List[UserContext] = []
        self.application: Application = ApplicationBuilder().token(settings.tg_bot_token).build()
        self.message_handler = MessageHandler(filters.ALL, self.process_update)

    async def process_update(self, update: Update):
        msg = update.message
        logger.info(f"Received message {msg.id} from {msg.from_user.name}:" f" {msg.voice=}, {msg.text=}")
        user = self.get_or_create_user(update.message.from_user)
        result = await user.process_reply(update)
        if result.response_message:
            await user.tg_user.send_message(
                text=result.response_message,
                reply_to_message_id=update.message.message_id,
            )

    def get_or_create_user(self, tg_user: User) -> UserContext:
        for user in self.user_contexts:
            if user.id == tg_user.id:
                return user
        new_user = UserContext(tg_user, registry)
        self.user_contexts.append(new_user)
        return new_user

    async def run_polling(self):
        updater = self.application.updater
        await updater.initialize()
        q = await updater.start_polling()
        while True:
            update = await q.get()
            if update and update.message:
                await self.process_update(update)
            await asyncio.sleep(0.1)
