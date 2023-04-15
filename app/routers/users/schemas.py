from pydantic import BaseModel, EmailStr, constr


class UserBase(BaseModel):
    name: constr(min_length=1, max_length=32)
    surname: constr(min_length=1, max_length=32)
    patronymic: constr(min_length=1, max_length=32)
    email: EmailStr
    phone_number: constr(min_length=11, max_length=11)


class UserCreate(UserBase):
    password: constr(min_length=1, max_length=16)


class User(UserBase):
    id: int
    games_played: int
    win_games: int
    is_organizer: bool
    team_id: int | None

    class Config:
        orm_mode = True
