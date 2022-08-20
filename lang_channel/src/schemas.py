from typing import Optional

from pydantic import BaseModel
from telegram import PhotoSize, Voice


class Post(BaseModel):
    text: Optional[str]
    photo: Optional[PhotoSize]
    voice: Optional[Voice]

    class Config:
        arbitrary_types_allowed = True

    def is_post_ready(self) -> bool:
        return all([self.text, self.photo, self.voice])


class FinishedPost(Post):
    id_: str

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_post_ready():
            raise Exception()  # TODO
