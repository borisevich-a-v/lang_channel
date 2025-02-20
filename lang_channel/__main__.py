from loguru import logger
from telegram.ext import ApplicationBuilder

from lang_channel import config, handlers

HANDLERS = (
    handlers.HELP_COMMAND,
    handlers.CREATE_POST_COMMAND,
    handlers.GET_NEXT_POSTS_REQUEST,
    handlers.POST_CREATE_CONVERSATION,
    handlers.PUBLISH_COMMAND,
    handlers.UNKNOWN_REQUEST,
)


def main():
    logger.info("Starting application...")

    application = ApplicationBuilder().token(config.TG_BOT_TOKEN).build()

    logger.info("Registering handlers...")
    for h in HANDLERS:
        application.add_handler(h)

    logger.info("Starting polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
