from loguru import logger

from .config import settings
from .google_sheets import SpreadSheet
from .telegram_bot.bot import LangBot


async def post_post(bot: LangBot, registry: SpreadSheet):
    post = registry.get_next_post_and_move_it_to_archive()
    logger.info(f"Post {post.id_} was downloaded")
    await bot.application.bot.send_photo(chat_id=settings.channel_name, photo=post.photo, caption=post.text)
    await bot.application.bot.send_voice(chat_id=settings.channel_name, voice=post.voice)
    logger.info(f"Post {post.id_} was sent")
