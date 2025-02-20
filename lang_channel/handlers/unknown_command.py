from telegram import Update
from telegram.ext import ContextTypes

message = """Не понимаю (,,>﹏<,,).\nВоспользуйтесь подсказкой: /help."""


async def process_unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(text=message)
