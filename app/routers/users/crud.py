from sqlalchemy.orm import Session
from app.sql import models
from app.routers.users import schemas
from passlib.context import CryptContext


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def check_email_in_users(db: Session, email: str):
    """ Проверят наличие переданного Email в базе данных.  """
    return db.query(db.query(models.User).filter(models.User.email == email).exists()).scalar()


def check_phone_number_in_users(db: Session, phone_number: str):
    """ Проверят наличие переданного номера телефона в базе данных.  """
    return db.query(db.query(models.User).filter(models.User.phone_number == phone_number).exists()).scalar()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # TODO: убрать костыль
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(**user.dict(exclude={"password"}), hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.id == user_id).one()
    db.delete(user)
    db.commit()
    return user
