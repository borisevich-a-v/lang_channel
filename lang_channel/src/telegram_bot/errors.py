# TODO choose better name
class CustomException(Exception):
    ...


class StorageError(CustomException):
    ...


class TelegramBotError(CustomException):
    ...


class BusinessLogicError(CustomException):
    ...
