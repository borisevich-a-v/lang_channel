import asyncio
import logging
from typing import Dict

import telegram
from fastapi import FastAPI

from post_creator_bot.src.config import settings
from post_creator_bot.src.google_sheets import registry
from post_creator_bot.src.post_post import post_post
from post_creator_bot.src.telegram_bot.bot import run_bot

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

app = FastAPI()
bot = telegram.Bot(token=settings.token)


@app.on_event("startup")
async def startup():
    asyncio.create_task(run_bot(bot))


@app.get("/")
async def get_status() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/publish_post", responses={200: {"description": "Post posted successfully"}})
async def publish_post() -> Dict[str, str]:
    await post_post(bot, registry)
    return {"description": "Post posted successfully"}
