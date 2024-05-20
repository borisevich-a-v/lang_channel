import asyncio
from typing import Dict

from fastapi import FastAPI
from loguru import logger

from bot import LangBot
from config import settings
from google_sheets import registry

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
    post = registry.get_next_post_and_move_it_to_archive()
    logger.info(f"Post {post.id_} was downloaded")
    await bot.application.bot.send_photo(chat_id=settings.channel_name, photo=post.photo, caption=post.text)
    await bot.application.bot.send_voice(chat_id=settings.channel_name, voice=post.voice)
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
