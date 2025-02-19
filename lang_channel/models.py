from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from telegram import PhotoSize, User, Voice


def get_uuid4_as_string() -> str:
    return str(uuid4())


@dataclass
class Post:
    id_: str = field(default_factory=get_uuid4_as_string)
    text: Optional[str] = None
    photo: Optional[PhotoSize] = None
    voice: Optional[Voice] = None
    publish_count: int = 0

    def is_ready(self) -> bool:
        return all([self.text, self.photo, self.voice])
