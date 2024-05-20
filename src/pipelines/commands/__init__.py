from abc import ABC
from re import Pattern

from pipelines import IPipeline


class ICommand(IPipeline, ABC):
    """Command is a single step pipline"""

    COMMAND: Pattern | str
