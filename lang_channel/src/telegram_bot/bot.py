import telegram
from telegram import Voice

from lang_channel.src.config import settings

bot = telegram.Bot(token=settings.token)
