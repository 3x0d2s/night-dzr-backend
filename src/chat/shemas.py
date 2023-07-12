from datetime import datetime
from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    chat_id: int
    user_id: int
    content_type: str
    text: str = Field(min_length=1, max_length=512)
    reply_to: int | None


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    date: datetime

    class Config:
        orm_mode = True
