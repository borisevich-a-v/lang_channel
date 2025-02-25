from loguru import logger
from telegram.ext import ContextTypes

from lang_channel import config
from lang_channel.storage.google_sheets import registry


async def publish_post(context: ContextTypes.DEFAULT_TYPE):
    logger.info("Publishing a post...")
    post = registry.get_next_post()
    if post is None:
        logger.info("Nothing to publish")
        return
    await context.bot.send_photo(chat_id=config.CHANNEL_ID, photo=post.photo, caption=post.text)
    await context.bot.send_voice(chat_id=config.CHANNEL_ID, voice=post.voice)
    post.publish_count = int(post.publish_count) + 1
    registry.archive_post(post)
    logger.info(f"Successfully published the post with id: {post.id_}")
