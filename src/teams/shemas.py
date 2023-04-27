from pydantic import BaseModel, Field


class TeamBase(BaseModel):
    pass


class TeamCreate(TeamBase):
    name: str = Field(min_length=1, max_length=32)


class TeamRead(TeamBase):
    id: int
    name: str
    games_played: int
    win_games: int

    class Config:
        orm_mode = True


class TeamUpdate(TeamBase):
    name: str | None
    games_played: int | None
    win_games: int | None
