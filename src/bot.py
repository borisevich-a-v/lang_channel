import asyncio
from typing import Dict

from loguru import logger
from telegram import Update, User
from telegram.ext import Application, ApplicationBuilder, MessageHandler, filters

from config import settings
from google_sheets import registry
from pipelines.comand_handler import UserContext


class LangBot:
    """
    Just wrapper to support legacy code (from 2019)
    It was designed for a few users
    """

    def __init__(self):
        self._user_contexts: Dict[int, UserContext] = {}
        self.application: Application = ApplicationBuilder().token(settings.tg_bot_token).build()
        self.message_handler = MessageHandler(filters.ALL, self.process_update)

    async def process_update(self, update: Update):
        logger.info(f"Received update from {update.effective_user}: {update}")
        user = self.get_or_create_user(update.effective_user)
        result = await user.process_reply(update)
        if result.response_message:
            await user.tg_user.send_message(text=result.response_message)

    def get_or_create_user(self, tg_user: User) -> UserContext:
        user = self._user_contexts.get(tg_user.id)
        if not user:
            user = UserContext(tg_user, registry)
            self._user_contexts[user.id] = user
        return user

    async def run(self):
        updater = self.application.updater
        await updater.initialize()
        q = await updater.start_polling()
        while True:
            update = await q.get()
            await self.process_update(update)
            await asyncio.sleep(0.07)
