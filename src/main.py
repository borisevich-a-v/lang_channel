from typing import Dict

from fastapi import BackgroundTasks, FastAPI
from loguru import logger

from bot import LangBot
from config import settings
from google_sheets import registry

web_app = FastAPI()
bot = LangBot()


@web_app.on_event("startup")
async def startup(background_tasks: BackgroundTasks):
    background_tasks.add_task(bot.run())


@web_app.get("/")
async def get_status() -> Dict[str, str]:
    logger.info("Request on endpoint `/`")
    return {"status": "ok"}


@web_app.post("/publish_post", responses={200: {"description": "Posted successfully"}})
async def publish_post() -> Dict[str, str]:
    logger.info("Request on endpoint `publish_post`")
    post = registry.get_next_post_and_move_it_to_archive()
    logger.info(f"Post {post.id_} was downloaded")
    await bot.application.bot.send_photo(chat_id=settings.channel_name, photo=post.photo, caption=post.text)
    await bot.application.bot.send_voice(chat_id=settings.channel_name, voice=post.voice)
    return {"description": "Post posted successfully"}
