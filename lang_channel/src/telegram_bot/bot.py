import asyncio
import traceback
from typing import AsyncIterator, List

import telegram
from telegram import Update
from telegram import User as TelegramUser

from lang_channel.src.comand_handlers import User
from lang_channel.src.google_sheets import registry

UPDATE_LIMIT = 5


async def get_updates(bot_instance) -> AsyncIterator[Update]:
    last_update_id = 0
    while True:
        try:
            updates = await bot_instance.get_updates(
                limit=UPDATE_LIMIT, offset=last_update_id if last_update_id else None
            )
        except telegram.error.TimedOut:
            # TODO FIX ME
            continue
        if not updates:
            await asyncio.sleep(0.1)
            continue
        for update in updates:
            last_update_id = max(last_update_id, update.update_id + 1)
            yield update


def get_or_create_user(tg_user: TelegramUser, users: List[User]) -> User:
    for user in users:
        if user.id == tg_user.id:
            return user
    new_user = User(tg_user, registry)
    users.append(new_user)
    return new_user


async def run_bot(bot):
    print("start")
    users = []
    async for update in get_updates(bot):
        try:
            print(update.message.text)
            user = get_or_create_user(update.message.from_user, users)
        except Exception:
            traceback.print_exc()
            continue
        try:
            result = await user.process_reply(update)
            if result.response_message:
                await user.tg_user.send_message(
                    text=result.response_message,
                    reply_to_message_id=update.message.message_id,
                )
        except Exception:
            traceback.print_exc()
            continue
