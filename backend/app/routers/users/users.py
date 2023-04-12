from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.sql import models
from app.routers.users import crud, schemas
from app.sql.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["Users"])


@router.post("/api/users", response_model=schemas.User, summary="Register User")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    check = crud.check_email_in_users(db, email=user.email)
    if check:
        raise HTTPException(status_code=400, detail="Email already registered.")
    check = crud.check_phone_number_in_users(db, phone_number=user.phone_number)
    if check:
        raise HTTPException(status_code=400, detail="Phone number already registered.")
    return crud.create_user(db=db, user=user)


@router.get("/api/users", response_model=schemas.User, summary="Get User")
def get_user(user_id: Annotated[int, Query(alias="id")], db: Session = Depends(get_db)):
    return crud.get_user(db, user_id)


@router.delete("/api/users", response_model=schemas.User, summary="Delete User")
def get_user(user_id: Annotated[int, Query(alias="id")], db: Session = Depends(get_db)):
    return crud.delete_user(db, user_id)
