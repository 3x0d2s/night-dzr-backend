from typing import Optional, Union
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, InvalidPasswordException

from src.auth.utils import get_user_db
from src.auth.models import User
from src.auth.schemas import UserCreate


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    # TODO: Реализовать сброс пароля и верификацию

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    async def on_after_login(self,
                             user: User,
                             request: Optional[Request] = None):
        print(f"User {user.id} logged in.")

    async def validate_password(self,
                                password: str,
                                user: Union[UserCreate, User]) -> None:
        if len(password) < 8:
            raise InvalidPasswordException(
                reason="Password should be at least 8 characters"
            )
        if user.email in password:
            raise InvalidPasswordException(
                reason="Password should not contain e-mail"
            )


async def get_user_manager(user_db=Depends(get_user_db)):
    yield UserManager(user_db)
