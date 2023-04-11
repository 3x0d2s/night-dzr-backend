from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.sql import crud, models, schemas
from app.sql.database import engine, get_db

models.Base.metadata.create_all(bind=engine)

router = APIRouter(tags=["Users"])


@router.post("/api/users/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered.")
    return crud.create_user(db=db, user=user)


# TODO: Удаление юзера

# TODO: Взятие данных юзера по ID
