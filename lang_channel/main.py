import asyncio
from random import randint
from typing import Dict

from fastapi import FastAPI
from loguru import logger
from src.google_sheets import registry
from src.post_post import post_post
from src.telegram_bot.bot import LangBot

app = FastAPI()
bot = LangBot()


@app.on_event("startup")
async def startup():
    asyncio.create_task(bot.run())


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


# @app.get("/notify_admin")
# async def check_and_notify_admin() -> Dict[str, str]:
#     logger.info("Request on endpoint `notify_admin`")
#     posts = registry.get_next_posts(4)
#     if len(posts) > 3:
#         return {"description": "post amount is decent"}
#     text = f"Hi! Could you add new post in post list? There are only {len(posts)} posts 😿"
#     await bot.send_message(chat_id=settings.admin_tg_id, text=text)
#     return {"description": "admin has been notified"}
