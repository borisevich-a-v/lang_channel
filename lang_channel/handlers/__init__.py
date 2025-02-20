from telegram.ext import CommandHandler, ConversationHandler, MessageHandler, filters

from .create_post.create_post import (
    APPROVE,
    APPROVED,
    DISAPPROVED,
    VOICE,
    PostTextFilter,
    process_approval,
    process_approval_not_provided,
    process_audio,
    process_audio_not_provided,
    process_begin_post_creating,
    process_cancel,
)
from .get_next_posts import GET_NEXT_POSTS_PATTERN, process_get_next_posts
from .help import process_help
from .publish_post import process_publish_post
from .unknown_command import process_unknown

HELP_COMMAND = CommandHandler("help", process_help)
CREATE_POST_COMMAND = CommandHandler("create_post", process_help)
CANCEL_COMMAND = CommandHandler("cancel", process_cancel)
PUBLISH_COMMAND = CommandHandler("publish_post", process_publish_post)

UNKNOWN_REQUEST = MessageHandler(None, process_unknown)
GET_NEXT_POSTS_REQUEST = MessageHandler(filters.Regex(GET_NEXT_POSTS_PATTERN), process_get_next_posts)


POST_CREATE_CONVERSATION = ConversationHandler(
    entry_points=[MessageHandler(PostTextFilter(), process_begin_post_creating)],
    states={  # pyright: ignore [reportArgumentType]
        VOICE: [
            CANCEL_COMMAND,
            MessageHandler(filters.VOICE, process_audio),
            MessageHandler(None, process_audio_not_provided),
        ],
        APPROVE: [
            CANCEL_COMMAND,
            MessageHandler(filters.Regex(f"^({APPROVED}|{DISAPPROVED})$"), process_approval),
            MessageHandler(None, process_approval_not_provided),
        ],
    },
    fallbacks=[CANCEL_COMMAND],  # pyright: ignore [reportArgumentType]
)
