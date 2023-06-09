from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.template_router import crud as user_crud
from src.auth import schemas as user_schemes
from src.database import get_db_session
from src.auth.auth import current_user
router = APIRouter(tags=["Users"])

# ВАЖНО
# Сейчас данные эндпоинты не используются, так как FastAPI-Users предоставляет
# готовое решение для всех эндпоинтов ниже, в проекте этот файл сохранён для примера того, как строятся эндпоинты


@router.get("/api/users", response_model=user_schemes.UserRead,
            summary="Get User", status_code=status.HTTP_200_OK)
async def get_user(user_id: Annotated[int, Query(alias="id")],
                   db: Annotated[AsyncSession, Depends(get_db_session)]):
    user = await user_crud.get_user_data(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id={user_id} not found.")
    return user


@router.post("/api/users", response_model=user_schemes.UserRead,
             summary="Register User", status_code=status.HTTP_201_CREATED)
async def create_user(user: Annotated[user_schemes.UserCreate, Body()],
                      db: Annotated[AsyncSession, Depends(get_db_session)]):
    email_exists = await user_crud.check_email_in_users(db, email=user.email)
    if email_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Email already registered.")
    phone_number_exists = await user_crud.check_phone_number_in_users(db, phone_number=user.phone_number)
    if phone_number_exists:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Phone number already registered.")
    return await user_crud.create_user(db=db, user=user)


@router.delete("/api/users", response_model=user_schemes.UserRead,
               summary="Delete User", status_code=status.HTTP_200_OK)
async def delete_user(user_id: Annotated[int, Query(alias="id")],
                      db: Annotated[AsyncSession, Depends(get_db_session)]):
    user = await user_crud.delete_user(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"User with id={user_id} not found.")
    return user


@router.get("/api/users/me/", response_model=user_schemes.UserRead,
            summary="Get Current User", status_code=status.HTTP_200_OK)
async def get_user_by_token(user: Annotated[user_schemes.UserRead, Depends(current_user)]):
    return user
