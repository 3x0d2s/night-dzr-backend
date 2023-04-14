from typing import Annotated
#
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import BaseModel
#
from app.data.config_reader import config
from app.routers.users import crud, schemas
from app.sql.database import get_db

router = APIRouter(tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get("/api/users", response_model=schemas.User, summary="Get User")
def get_user(user_id: Annotated[int, Query(alias="id")], db: Session = Depends(get_db)):
    return crud.get_user(db, user_id)


@router.post("/api/users", response_model=schemas.User, summary="Register User")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    check = crud.check_email_in_users(db, email=user.email)
    if check:
        raise HTTPException(status_code=400, detail="Email already registered.")
    check = crud.check_phone_number_in_users(db, phone_number=user.phone_number)
    if check:
        raise HTTPException(status_code=400, detail="Phone number already registered.")
    return crud.create_user(db=db, user=user)


@router.delete("/api/users", response_model=schemas.User, summary="Delete User")
def get_user(user_id: Annotated[int, Query(alias="id")], db: Session = Depends(get_db)):
    return crud.delete_user(db, user_id)


class TokenData(BaseModel):
    user_id: int | None = None


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_db)):
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
    user = crud.get_user(db, user_id=token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


@router.get("/api/users/me/", response_model=schemas.User, summary="Get Current User")
def read_users_me(current_user: Annotated[schemas.User, Depends(get_current_user)]):
    return current_user
