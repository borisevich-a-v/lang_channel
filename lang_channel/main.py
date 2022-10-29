import asyncio
from random import randint
from typing import Dict

import telegram
from fastapi import FastAPI
from loguru import logger
from src.config import settings
from src.google_sheets import registry
from src.post_post import post_post
from src.telegram_bot.bot import run_bot

logger.remove()
logger.configure(handlers=[dict(sink="/logs.log")])

app = FastAPI()
bot = telegram.Bot(token=settings.tg_bot_token)


@app.on_event("startup")
async def startup():
    asyncio.create_task(run_bot(bot))


@app.get("/")
async def get_status() -> Dict[str, str]:
    logger.info("Request on endpoint `/`")
    return {"status": "ok"}


@app.post("/publish_post", responses={200: {"description": "Post posted successfully"}})
async def publish_post() -> Dict[str, str]:
    logger.info("Request on endpoint `publish_post`")
    magic_number_min, magic_number_max = 10, 3 * 60
    time_to_sleep = randint(magic_number_min, magic_number_max)
    await asyncio.sleep(time_to_sleep)
    await post_post(bot, registry)
    return {"description": "Post posted successfully"}
