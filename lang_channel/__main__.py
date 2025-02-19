from typing import Callable

from loguru import logger
from telegram.ext import ApplicationBuilder, CommandHandler

from lang_channel import config, handlers

COMMAND_HANDLERS: dict[str, Callable] = {
    "start": handlers.start,
    "help": handlers.help_,
}


def main():
    logger.info("Starting application...")
    application = ApplicationBuilder().token(config.TG_BOT_TOKEN).build()

    for command_name, command_handler in COMMAND_HANDLERS.items():
        application.add_handler(CommandHandler(command_name, command_handler))

    logger.info("Starting polling...")
    application.run_polling()


if __name__ == "__main__":
    main()
