import asyncio
import logging
from random import randint
from typing import Dict

import telegram
from fastapi import FastAPI
from src.config import settings
from src.google_sheets import registry
from src.post_post import post_post
from src.telegram_bot.bot import run_bot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

app = FastAPI()
bot = telegram.Bot(token=settings.tg_bot_token)


@app.on_event("startup")
async def startup():
    asyncio.create_task(run_bot(bot))


@app.get("/")
async def get_status() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/publish_post", responses={200: {"description": "Post posted successfully"}})
async def publish_post() -> Dict[str, str]:
    magic_number_min, magic_number_max = 10, 7 * 60
    time_to_sleep = randint(magic_number_min, magic_number_max)
    await asyncio.sleep(time_to_sleep)
    await post_post(bot, registry)
    return {"description": "Post posted successfully"}
