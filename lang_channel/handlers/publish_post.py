from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from lang_channel import config
from lang_channel.storage.google_sheets import registry


async def process_publish_post(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Publishing a post...")
    try:
        post = registry.get_next_posts(1)[0]
    except IndexError:
        await update.message.reply_text("No posts to publish")
        return

    logger.info(f"Post {post.id_} has been downloaded")
    await context.bot.send_photo(chat_id=config.CHANNEL_ID, photo=post.photo, caption=post.text)
    await context.bot.send_voice(chat_id=config.CHANNEL_ID, voice=post.voice)
    logger.info(f"Post {post.id_} has been published")

    post.publish_count += 1

    registry.archive_post(post)
    logger.info(f"Post {post.id_} has been archived")

    await update.message.reply_text(text="Пост опубликован.")
