from abc import ABC
from re import Pattern
from typing import Union

from src.pipelines.interfaces import IPipeline


class ICommand(IPipeline, ABC):
    """Command is a single step pipline"""

    COMMAND: Union[Pattern, str]
