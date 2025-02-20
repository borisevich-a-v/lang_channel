import re

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from lang_channel.helpers.get_chat_id import get_chat_id
from lang_channel.storage.google_sheets import registry

GET_NEXT_POSTS_PATTERN = re.compile(r"/get_[0-9]{1,5}_next_posts")


def parse_post_amount(command) -> int:
    amount = int(command.lstrip("/get_").rstrip("_next_posts"))
    if amount < 1:
        amount = 1
    if amount > 20:
        amount = 20

    return amount


async def process_get_next_posts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.info("Getting posts for command {}", update.message.text)
    posts_amount = parse_post_amount(update.message.text)
    chat_id = get_chat_id(update)
    posts = registry.get_next_posts(posts_amount)
    if not posts:
        await context.bot.send_message(chat_id, "В запасе не осталось новых постов.")
    for i, post in enumerate(posts, start=1):
        await context.bot.send_message(chat_id, text=f"{'=' * 10}Пост {i}{'='*10}")
        await context.bot.send_photo(chat_id, photo=post.photo, caption=post.text)
        await context.bot.send_voice(chat_id, voice=post.voice)
