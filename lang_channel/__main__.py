import asyncio
from typing import Dict

from loguru import logger

import config
from lang_channel.bot import LangBot
from lang_channel.google_sheets import registry


async def publish_post() -> Dict[str, str]:
    logger.info("Request on endpoint `publish_post`")
    post = registry.get_next_post_and_move_it_to_archive()
    logger.info(f"Post {post.id_} was downloaded")
    await bot.application.bot.send_photo(chat_id=config.CHANNEL_NAME, photo=post.photo, caption=post.text)
    await bot.application.bot.send_voice(chat_id=config.CHANNEL_NAME, voice=post.voice)
    return {"description": "Post posted successfully"}


if __name__ == "__main__":
    logger.info("Starting application...")

    event_loop = asyncio.new_event_loop()

    bot = LangBot()
    bot_task = event_loop.create_task(bot.run())

    logger.info("The infinite loop is running")
    event_loop.run_forever()
