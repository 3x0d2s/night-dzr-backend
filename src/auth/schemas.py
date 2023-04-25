from fastapi_users import schemas
from pydantic import EmailStr, constr


class UserBase(schemas.BaseUser[int]):
    id: int
    name: constr(min_length=1, max_length=32)
    surname: constr(min_length=1, max_length=32)
    patronymic: constr(min_length=1, max_length=32)
    email: EmailStr
    phone_number: constr(min_length=11, max_length=11)
    is_active: bool = True
    is_superuser: bool = False
    is_verified: bool = False


class UserCreate(schemas.BaseUserCreate):
    name: constr(min_length=1, max_length=32)
    surname: constr(min_length=1, max_length=32)
    patronymic: constr(min_length=1, max_length=32)
    email: EmailStr
    phone_number: constr(min_length=11, max_length=11)
    password: str
    is_active: bool | None = True
    is_superuser: bool | None = False
    is_verified: bool | None = False


class UserRead(UserBase):
    games_played: int
    win_games: int
    team_id: int | None


class UserUpdate(schemas.BaseUserUpdate):
    name: constr(min_length=1, max_length=32) | None
    surname: constr(min_length=1, max_length=32) | None
    patronymic: constr(min_length=1, max_length=32) | None
    phone_number: constr(min_length=11, max_length=11) | None
    password: str | None
    email: EmailStr | None
    games_played: int | None
    win_games: int | None
    team_id: int | None
    is_active: bool | None
    is_superuser: bool | None
    is_verified: bool | None
