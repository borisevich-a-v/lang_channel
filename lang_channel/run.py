import asyncio
import logging
import traceback
from typing import AsyncIterator, List

import telegram
from telegram import Update
from telegram import User as TelegramUser

from lang_channel.src.comand_handlers import User
from lang_channel.src.google_sheets import registry
from lang_channel.src.telegram_bot.bot import bot

UPDATE_LIMIT = 5

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)


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


async def main():
    print("start")
    path = "11.png"
    users = []
    async for update in get_updates(bot):
        print(update)
        user = get_or_create_user(update.message.from_user, users)
        try:
            result = await user.process_reply(update)
            if result.response_message:
                await user.tg_user.send_message(
                    text=result.response_message,
                    reply_to_message_id=update.message.message_id,
                )
        except Exception as exp:
            traceback.print_exc()
            continue


# post = create_post(update)
#             post[1].save(path)
#             await bot.send_photo(chat_id=update.message.chat_id, photo=open(path, 'rb'), caption=post[0])

if __name__ == "__main__":
    asyncio.run(main())
    ...
