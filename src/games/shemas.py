from datetime import datetime
from pydantic import BaseModel, Field


class GameBase(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    legend: str = Field(min_length=1, max_length=512)
    datetime_start: datetime
    datetime_end: datetime


class GameCreate(GameBase):
    pass


class GameRead(GameBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class GameUpdate(GameBase):
    name: str | None = Field(min_length=1, max_length=64)
    legend: str | None = Field(min_length=1, max_length=512)
    datetime_start: datetime | None
    datetime_end: datetime | None
