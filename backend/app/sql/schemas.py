from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    name: str
    surname: str
    patronymic: str
    email: EmailStr
    phone_number: constr(min_length=11, max_length=11)
    games_played: int
    win_games: int
    is_organizer: bool
    team_id: int | None


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int

    class Config:
        orm_mode = True
