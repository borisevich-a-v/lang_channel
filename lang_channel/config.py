import datetime
import os

from dotenv import load_dotenv

load_dotenv()

DEVELOPER_TG_ID = "240856036"  # my telegram
ADMIN_TG_ID = "1292759426"
ALLOWED_USERS = (DEVELOPER_TG_ID, ADMIN_TG_ID)

TG_BOT_TOKEN: str = os.environ["tg_bot_token"]

CHANNEL_ID: str = os.environ["channel_id"]

SPREADSHEET_NAME = os.getenv("spreadsheet_name", "post_list")
NEW_POSTS_TABLE_NAME = "posts"
ARCHIVE_TABLE_NAME = "archive"

POST_PUBLISHING_TIME = datetime.time(hour=8, minute=0, tzinfo=datetime.timezone(datetime.timedelta(hours=3)))
