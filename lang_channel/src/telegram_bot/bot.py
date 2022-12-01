from typing import Dict

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
        self.user_contexts: Dict[int, UserContext] = {}
        self.application: Application = ApplicationBuilder().token(settings.tg_bot_token).build()
        self.message_handler = MessageHandler(filters.ALL, self.process_update)

    async def process_update(self, update: Update):
        logger.info(f"Received update from {update.effective_user}: {update}")
        # Need to refactor users if users amount is huge
        user = self.get_or_create_user(update.effective_user)
        result = await user.process_reply(update)
        if result.response_message:
            await user.tg_user.send_message(text=result.response_message)

    def get_or_create_user(self, tg_user: User) -> UserContext:
        user = self.user_contexts.get(tg_user.id)
        if not user:
            user = UserContext(tg_user, registry)
            self.user_contexts[user.id] = user
        return user

    async def run(self):
        updater = self.application.updater
        await updater.initialize()
        q = await updater.start_polling()
        while True:
            update = await q.get()
            await self.process_update(update)
