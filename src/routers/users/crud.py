from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from src.sql import models
from src.routers.users import schemas


async def get_user(db: AsyncSession, user_id: int):
    query = select(models.User).filter(models.User.id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.scalars().first()


async def check_email_in_users(db: AsyncSession, email: str):
    """ Проверяет наличие переданного Email в базе данных.  """
    query = exists(1).select_from(models.User).where(models.User.email == email).select()
    curr = await db.execute(query)
    await db.commit()
    result = curr.scalar_one()
    return result


async def check_phone_number_in_users(db: AsyncSession, phone_number: str):
    """ Проверят наличие переданного номера телефона в базе данных.  """
    query = exists(1).select_from(models.User).where(models.User.phone_number == phone_number).select()
    curr = await db.execute(query)
    await db.commit()
    result = curr.scalar_one()
    return result


async def get_user_by_email(db: AsyncSession, email: str):
    query = select(models.User).filter(models.User.email == email)
    result = await db.execute(query)
    await db.commit()
    return result.scalars().first()


async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100):
    query = select(models.User).offset(skip).limit(limit)
    result = await db.execute(query)
    await db.commit()
    return result.scalars().all()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  # TODO: убрать костыль
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(**user.dict(exclude={"password"}), hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    query = select(models.User).filter(models.User.id == user_id)
    user = await db.execute(query)
    user = user.scalars().first()
    if user:
        await db.delete(user)
        await db.commit()
        return user
    else:
        return None
