from telegram import Bot

from lang_channel.src.config import settings
from lang_channel.src.google_sheets import SpreadSheet


async def post_post(bot: Bot, registry: SpreadSheet):
    post = registry.get_next_post_and_move_it_to_archive()
    await bot.send_photo(chat_id=settings.channel, photo=post.photo, caption=post.text)
    await bot.send_voice(chat_id=settings.channel, voice=post.voice)
