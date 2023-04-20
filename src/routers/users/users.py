from typing import Annotated
#
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from pydantic import BaseModel
#
from config.config_reader import config
from src.routers.users import crud, schemas
from src.sql.database import get_db

router = APIRouter(tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/api/users", response_model=schemas.User, summary="Get User", status_code=status.HTTP_200_OK)
async def get_user(user_id: Annotated[int, Query(alias="id")],
                   db: Annotated[AsyncSession, Depends(get_db)]):
    user = await crud.get_user_data(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id={user_id} not found.")
    return user


@router.post("/api/users", response_model=schemas.User, summary="Register User", status_code=status.HTTP_201_CREATED)
async def create_user(user: Annotated[schemas.UserCreate, Body()],
                      db: Annotated[AsyncSession, Depends(get_db)]):
    email_exists = await crud.check_email_in_users(db, email=user.email)
    if email_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered.")
    phone_number_exists = await crud.check_phone_number_in_users(db, phone_number=user.phone_number)
    if phone_number_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Phone number already registered.")
    return await crud.create_user(db=db, user=user)


@router.delete("/api/users", response_model=schemas.User, summary="Delete User", status_code=status.HTTP_200_OK)
async def delete_user(user_id: Annotated[int, Query(alias="id")],
                      db: Annotated[AsyncSession, Depends(get_db)]):
    user = await crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id={user_id} not found.")
    return user


class TokenData(BaseModel):
    user_id: int | None = None


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],
                           db: Annotated[AsyncSession, Depends(get_db)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECURITY_KEY.get_secret_value(), algorithms=[config.TOKEN_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=int(user_id))
    except JWTError:
        raise credentials_exception
    user = await crud.get_user_data(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


@router.get("/api/users/me/", response_model=schemas.User, summary="Get Current User", status_code=status.HTTP_200_OK)
async def get_user_by_token(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return current_user
