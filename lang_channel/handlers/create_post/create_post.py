import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from loguru import logger
from telegram import Message, ReplyKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler
from telegram.ext.filters import MessageFilter

from lang_channel.handlers.create_post.validators import ValidationError, validate_hashtags
from lang_channel.helpers.get_chat_id import get_chat_id
from lang_channel.models import Post
from lang_channel.preview.get_preview import PreviewError, get_preview
from lang_channel.storage.google_sheets import PostNotSaved, registry

VOICE, APPROVE = range(2)

APPROVED, DISAPPROVED, CANCEL = "Норм", "Надо переделать", "/cancel"

user_to_post_map: dict[int, Post] = {}


class PostTextFilter(MessageFilter):
    def filter(self, message: Message) -> bool:
        # Text for post contains 4 rows exactly
        return len(message.text.split("\n")) == 4


def create_and_save_preview(text: str, dir_to_save: Path) -> Path:
    preview = get_preview(text)
    preview_path = dir_to_save / f"{hashlib.sha256(text.encode()).hexdigest()}.jpg"
    preview.save(preview_path)
    return preview_path


async def process_begin_post_creating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        ch_text, ru_text, transcription, hashtags = update.message.text.split("\n")
    except ValueError as exp:
        await update.message.reply_text("Для создания поста вам нужно отправить четыре строки.")
        raise ValueError("Unfortunately you have to send exactly 4 lines") from exp

    try:
        validate_hashtags(hashtags)
    except ValidationError as exp:
        await update.message.reply_text(str(exp))
        return ConversationHandler.END

    post = Post()
    user_to_post_map[get_chat_id(update)] = post

    with TemporaryDirectory() as tmpdir:
        try:
            preview_path = create_and_save_preview(ch_text, Path(tmpdir))
        except PreviewError as exp:
            await update.message.reply_text(str(exp))
            return ConversationHandler.END
        with open(preview_path, "rb") as fout:
            photo = await context.bot.send_photo(chat_id=get_chat_id(update), photo=fout)
            post.photo = photo.photo[0]

    ch_text = ch_text.replace("\\n", " ")
    ch_text = f"🇨🇳 {ch_text}"
    ru_text = f"🇷🇺 {ru_text}"
    transcription = f"🗣 {transcription}"

    post.text = "\n\n".join([ch_text, ru_text, transcription, hashtags])

    await update.message.reply_text("Теперь запишите аудио.")

    return VOICE


async def process_audio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Processing audio...")
    post = user_to_post_map[get_chat_id(update)]

    post.voice = update.message.voice

    if not post.voice or not post.photo:
        await context.bot.send_message(get_chat_id(update), "there is some problem, post creation was canceled")
        await process_cancel(update, context)
        return ConversationHandler.END

    await context.bot.send_photo(get_chat_id(update), post.photo, post.text)
    await context.bot.send_voice(get_chat_id(update), post.voice)

    reply_keyboard = [[APPROVED, DISAPPROVED, CANCEL]]
    await context.bot.send_message(
        chat_id=get_chat_id(update),
        text="Теперь проверьте, что с постом в целом все хорошо.",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="Норм или переделать?"
        ),
    )

    return APPROVE


async def process_audio_not_provided(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("User sent not an audio...")
    await update.message.reply_text(
        "Вы сейчас находитесь в процессе создания поста.\n"
        "Для продолжения необходимо отправить запись голоса\n"
        "Если вы хотите отменить создание, то отправьте команду /cancel."
    )

    return VOICE


async def process_approval(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info(f"Post was {update.message.text}. Processing...")
    if update.message.text == APPROVED:
        user = get_chat_id(update)
        try:
            registry.save_new_post(user_to_post_map[user].cook_post())
        except PostNotSaved as exp:
            await update.message.reply_text(str(exp))
            return ConversationHandler.END
        await update.message.reply_text("Пост сохранён.")
        user_to_post_map.pop(user)
    elif update.message.text == DISAPPROVED:
        await process_cancel(update, context)

    return ConversationHandler.END


async def process_approval_not_provided(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("User sent not an approval...")
    await update.message.reply_text(
        "Вы сейчас находитесь в процессе создания поста.\n"
        "Пожалуйста воспользуйтесь клавиатурой для того, чтобы подтвердить или отменить сохранение поста\n"
        "Если вы хотите отменить, то отправьте команду /cancel."
    )

    return APPROVE


async def process_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    logger.info("Canceling post creation...")
    user = get_chat_id(update)
    user_to_post_map.pop(user)
    await update.message.reply_text("Создание поста прекращено. Вы можете начать с начала.")

    return ConversationHandler.END
