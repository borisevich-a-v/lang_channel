from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings

dotenv_path = Path(__file__).parents[1] / ".env"

developer_tg_id = "240856036"  # my telegram
admin_tg_id = "1292759426"


class Settings(BaseSettings):
    tg_bot_token: str
    channel_name: str
    spreadsheet_name: str = "post_list"
    allowed_users: List[str] = [
        developer_tg_id,
        admin_tg_id,
    ]
    admin_tg_id: str = admin_tg_id
    data_time_format: str = "%Y/%m/%d, %H:%M:%S"

    class Config:
        env_file = dotenv_path
        env_file_encoding = "utf-8"


settings = Settings()
