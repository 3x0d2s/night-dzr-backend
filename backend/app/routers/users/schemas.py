from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    name: str
    surname: str
    patronymic: str
    email: EmailStr
    phone_number: constr(min_length=11, max_length=11)


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    games_played: int
    win_games: int
    is_organizer: bool
    team_id: int | None

    class Config:
        orm_mode = True
