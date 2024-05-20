from loguru import logger


class ValidationError(Exception):
    pass


def validate_hashtags(text: str):
    logger.info("Validating hashtags")
    validate_single_line(text)
    validate_all_words_starts_with_hash(text)
    validate_hashtag_amount(text)
    validate_case(text)


def validate_single_line(text: str):
    if "\n" in text:
        raise ValidationError("Hashtags should be on one line")


def validate_all_words_starts_with_hash(text: str):
    words = text.split()
    for word in words:
        if not word.startswith("#"):
            raise ValidationError(f"All hashtags have to be started with `#`, but you add: {word}")


def validate_hashtag_amount(text: str):
    if len(text.split()) > 4:
        raise ValidationError("Too many hashtags")


def validate_case(text: str):
    hashtags = text.split()
    for hashtag in hashtags:
        hashtag = hashtag.lstrip("#")
        if hashtag.capitalize() != hashtag:
            raise ValidationError("Hashtag has to be started with capitalize letter")
