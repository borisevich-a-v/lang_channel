from loguru import logger
from telegram.ext import ApplicationBuilder

from lang_channel import config, handlers
from lang_channel.jobs.publish_post import publish_post

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

    logger.info("Adding jobs...")
    application.job_queue.run_daily(publish_post, time=config.POST_PUBLISHING_TIME)

    logger.info("Starting polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
