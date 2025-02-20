from telegram import Update
from telegram.ext import ContextTypes

from lang_channel.helpers.get_chat_id import get_chat_id

message = r"""Для того чтобы записать пост просто отправь 4 строки вот в таком формате:

<строка1> Текст на китайском языке
<строка2> Перевод на русский
<строка3> Пиньинь
<строка4> Хэштеги

Если ты хочешь вставить текст на китайском, состоящий из двух строк, то вместо переноса строки вставь `\n`
"""


async def process_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await context.bot.send_message(chat_id=get_chat_id(update), text=message)
