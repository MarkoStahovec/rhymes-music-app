from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class PostSong(BaseModel):
    name: str
    author: str
    track: bytes

    class Config:
        orm_mode = True


class GetAllSongs(BaseModel):
    song_id: int
    name: str
    author: str
    uploaded_at: datetime


class SongInfo(BaseModel):
    name: str
    author: str

