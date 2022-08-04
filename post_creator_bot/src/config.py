from pathlib import Path
from typing import List

from pydantic import BaseSettings, Field

dotenv_path = Path(__file__).parents[1] / ".env"


class Settings(BaseSettings):
    token: str = Field(..., env="TG_BOT_TOKEN")
    channel: str
    spreadsheet_name: str = "post_list"
    allowed_users: List[str] = [
        "240856036",
        "1292759426",
    ]  # the first id is my telegram
    str_fmt = "%Y/%m/%d, %H:%M:%S"

    class Config:
        env_file = dotenv_path
        env_file_encoding = "utf-8"


settings = Settings()
