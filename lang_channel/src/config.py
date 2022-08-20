from pathlib import Path
from typing import List

from pydantic import BaseSettings

dotenv_path = Path(__file__).parents[1] / ".env"


class Settings(BaseSettings):
    tg_bot_token: str
    channel_name: str
    spreadsheet_name: str = "post_list"
    allowed_users: List[str] = [
        "240856036",  # my telegram
        "1292759426",
    ]
    data_time_format = "%Y/%m/%d, %H:%M:%S"

    class Config:
        env_file = dotenv_path
        env_file_encoding = "utf-8"


settings = Settings()
