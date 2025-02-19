from telegram import Update
from telegram.ext import ContextTypes

from lang_channel.helpers.get_chat_id import get_chat_id

message = """Синь добавит текст инструкции
"""


async def help_(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=get_chat_id(update), text=message)
