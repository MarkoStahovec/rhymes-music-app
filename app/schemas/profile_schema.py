from pydantic import BaseModel
from datetime import datetime, date
from typing import Optional


class GetProfileId(BaseModel):
    user_id: int
    email: str
    nickname: str
    registered_at: datetime
