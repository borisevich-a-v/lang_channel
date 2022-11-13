from typing import Optional
from uuid import uuid4

from pydantic import BaseModel
from telegram import PhotoSize, User, Voice


class Post(BaseModel):
    text: Optional[str]
    photo: Optional[PhotoSize]
    voice: Optional[Voice]

    class Config:
        arbitrary_types_allowed = True

    async def send_to_user(self, user: User) -> None:
        if not self.is_ready():
            raise ValueError("Post is not ready")
        await user.send_photo(photo=self.photo, caption=self.text)
        await user.send_voice(voice=self.voice)

    def is_ready(self) -> bool:
        return all([self.text, self.photo, self.voice])


class RawPost(Post):
    ...


class FinishedPost(Post):
    id_: str
    text: str
    photo: PhotoSize
    voice: Voice

    @classmethod
    def parse_raw_post(cls, raw_post: RawPost):
        if raw_post.is_ready():
            return cls(id_=str(uuid4()), text=raw_post.text, photo=raw_post.photo, voice=raw_post.voice)
