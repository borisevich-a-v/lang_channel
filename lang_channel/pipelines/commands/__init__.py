from abc import ABC
from re import Pattern

from lang_channel.pipelines import IPipeline


class ICommand(IPipeline, ABC):
    """Command is a single step pipline"""

    COMMAND: Pattern | str
