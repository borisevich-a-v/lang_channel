from typing import Callable

from loguru import logger
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

from lang_channel import config, handlers
from lang_channel.handlers.get_next_posts import GET_NEXT_POSTS_PATTERN, get_next_posts


def main():
    logger.info("Starting application...")

    application = ApplicationBuilder().token(config.TG_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("help", handlers.help_))

    application.add_handler(MessageHandler(filters.Regex(GET_NEXT_POSTS_PATTERN), get_next_posts))

    logger.info("Starting polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
