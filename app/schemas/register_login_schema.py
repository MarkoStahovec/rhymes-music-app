from pydantic import BaseModel


class UserRegister(BaseModel):
    email: str
    nickname: str
    password: str


class PostRegister(BaseModel):
    email: str
    nickname: str
    password: str

    class Config:
        orm_mode = True


class PostLogin(BaseModel):
    email: str
    password: str
