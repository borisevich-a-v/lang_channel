from typing import Optional
from uuid import uuid4

from pydantic import BaseModel
from telegram import PhotoSize, Voice

print("delete me")

class RawPost(BaseModel):
    text: Optional[str]
    photo: Optional[PhotoSize]
    voice: Optional[Voice]

    class Config:
        arbitrary_types_allowed = True

    def is_ready(self) -> bool:
        return all([self.text, self.photo, self.voice])


class FinishedPost(RawPost):
    id_: str
    text: str
    photo: PhotoSize
    voice: Voice

    @classmethod
    def parse_raw_post(cls, raw_post: RawPost):
        return cls(id_=str(uuid4()), text=raw_post.text, photo=raw_post.photo, voice=raw_post.voice)
