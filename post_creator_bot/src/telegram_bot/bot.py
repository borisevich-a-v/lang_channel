import telegram

from post_creator_bot.src.config import settings

bot = telegram.Bot(token=settings.token)
