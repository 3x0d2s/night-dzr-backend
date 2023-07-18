from pydantic import BaseModel, Field


class MessageBase(BaseModel):
    chat_id: int
    content_type: str
    text: str = Field(min_length=1, max_length=512)
    reply_to: int | None


class MessageCreate(MessageBase):
    pass


class MessageRead(MessageBase):
    id: int
    user_id: int
    date: float

    class Config:
        orm_mode = True


class ChatRead(BaseModel):
    id: int
    game_id: int
    team_id: int
    team_name: str
