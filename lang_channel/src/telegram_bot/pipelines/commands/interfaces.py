from abc import ABC
from re import Pattern
from typing import Union

from src.telegram_bot.pipelines.interfaces import IPipeline


class ICommand(IPipeline, ABC):
    """Command is a single step pipline"""
    HANDLER: Union[Pattern, str]
