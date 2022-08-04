from pydantic import BaseModel
from telegram import PhotoSize, Voice


class Post(BaseModel):
    text: str
    photo: PhotoSize
    voice: Voice

    class Config:
        arbitrary_types_allowed = True
