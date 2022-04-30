from pydantic import BaseModel


class LikeSongIn(BaseModel):
    song_id: int

    class Config:
        orm_mode = True


class LikeSong(BaseModel):
    user_id: int
    song_id: int

    class Config:
        orm_mode = True
