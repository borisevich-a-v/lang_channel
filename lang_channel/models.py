from dataclasses import dataclass, field
from typing import Optional
from uuid import uuid4

from telegram import PhotoSize, Voice


def get_uuid4_as_string() -> str:
    return str(uuid4())


@dataclass
class CookedPost:
    id_: str
    text: str
    photo: PhotoSize
    voice: Voice
    publish_count: int


@dataclass
class Post:
    id_: str = field(default_factory=get_uuid4_as_string)
    text: Optional[str] = None
    photo: Optional[PhotoSize] = None
    voice: Optional[Voice] = None
    publish_count: int = 0

    def cook_post(self) -> CookedPost:
        if not all([self.text is not None, self.photo is not None, self.voice is not None]):
            raise ValueError(f"Post is not ready: {Post}")
        return CookedPost(**{k: v for k, v in self.__dict__.items()})
