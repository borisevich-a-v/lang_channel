from loguru import logger


class ValidationError(Exception):
    ...


forbidden_hashtags = {"#Документ", "#Путешествия"}


def validate_hashtags(text: str):
    logger.info("Validating hashtags")
    validate_single_line(text)
    validate_all_words_starts_with_hash(text)
    validate_hashtag_amount(text)
    validate_case(text)
    validate_forbidden_hashtags(text)


def validate_single_line(text: str):
    if "\n" in text:
        raise ValidationError("Hashtags has to be one line")


def validate_all_words_starts_with_hash(text: str):
    words = text.split()
    for word in words:
        if not word.startswith("#"):
            raise ValidationError("All hashtags have to be started with `#`")


def validate_hashtag_amount(text: str):
    if len(text.split()) > 4:
        raise ValidationError("Too many hashtags")


def validate_case(text: str):
    hashtags = text.split()
    for hashtag in hashtags:
        hashtag = hashtag.lstrip("#")
        if hashtag.capitalize() != hashtag:
            raise ValidationError("Hashtag has to be started with capitalize letter")


def validate_forbidden_hashtags(text: str):
    for hashtag in text.split():
        if hashtag in forbidden_hashtags:
            raise ValidationError("Hmm, this hashtag is forbidden")
