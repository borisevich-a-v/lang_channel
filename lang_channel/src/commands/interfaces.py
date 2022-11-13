from abc import ABC, abstractmethod
from typing import Optional

from src.common import Result
from telegram import Update


class IHandler(ABC):
    @abstractmethod
    async def execute(self, update: Update) -> Optional[Result]:
        ...


class IPipeline(ABC):
    @abstractmethod
    async def handle_request(self, update: Update) -> Optional[Result]:
        ...
