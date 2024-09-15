import asyncio
from typing import Dict, NoReturn

from loguru import logger
from telegram import Bot, Update, User
from telegram.error import Forbidden, NetworkError

from google_sheets import registry
from pipelines.comand_handler import UserContext


class UserContextManager:
    def __init__(self):
        self._user_contexts: Dict[int, UserContext] = {}

    def get_user(self, tg_user: User) -> UserContext:
        user = self._user_contexts.get(tg_user.id)
        if user is None:
            user = UserContext(tg_user, registry)
            self._user_contexts[user.id] = user
        return user


class LangBot:
    """
    Just wrapper to support legacy code (from 2019).
    And this wrapper was created in 2022. I changed the framework again in 2024, so even this wrapper is ugly (-_-)
    """

    def __init__(self):
        self.user_context_manager = UserContextManager()

    async def process_updates(self, bot, update_id: int):
        updates = await bot.get_updates(offset=update_id, timeout=10, allowed_updates=Update.ALL_TYPES)
        for update in updates:
            next_update_id = update.update_id + 1
            if update.message and update.message.text:
                logger.info("Found message %s", update.message.text)
                user = self.user_context_manager.get_user(update.effective_user)
                result = await user.process_reply(update)
                if result.response_message:
                    await user.tg_user.send_message(text=result.response_message)

            return next_update_id
        return update_id

    async def run(self) -> NoReturn:
        async with Bot("TOKEN") as bot:
            try:
                update_id = (await bot.get_updates())[0].update_id
            except IndexError:
                update_id = None

            logger.info("listening for new messages...")
            while True:
                try:
                    update_id = await self.process_updates(bot, update_id)
                except NetworkError:
                    logger.error("Network error...")
                    await asyncio.sleep(1)
                except Forbidden:
                    logger.error("The user has blocked the bot.")
                    update_id += 1
