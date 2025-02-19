import os

from dotenv import load_dotenv

load_dotenv()

DEVELOPER_TG_ID = "240856036"  # my telegram
ADMIN_TG_ID = "1292759426"
ALLOWED_USERS = (DEVELOPER_TG_ID, ADMIN_TG_ID)

TG_BOT_TOKEN = os.getenv("tg_bot_token")

CHANNEL_NAME = os.getenv("channel_name")

SPREADSHEET_NAME = os.getenv("spreadsheet_name", "post_list")
NEW_POSTS_TABLE_NAME = "posts"
ARCHIVE_TABLE_NAME = "archive"

DATE_TIME_FORMAT = os.getenv("date_time_format", "%Y/%m/%d, %H:%M:%S")
