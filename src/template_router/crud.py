from sqlalchemy import select, exists
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from src.auth.models import User


async def get_user_data(db: AsyncSession, user_id: int):
    """ Возвращает данные юзера.  """
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    await db.commit()
    return result.scalars().first()


async def check_email_in_users(db: AsyncSession, email: str):
    """ Проверяет наличие переданного Email в базе данных.  """
    query = exists(1).select_from(User).where(User.email == email).select()
    curr = await db.execute(query)
    await db.commit()
    result = curr.scalar_one()
    return result


async def check_phone_number_in_users(db: AsyncSession, phone_number: str):
    """ Проверят наличие переданного номера телефона в базе данных.  """
    query = exists(1).select_from(User).where(User.phone_number == phone_number).select()
    curr = await db.execute(query)
    await db.commit()
    result = curr.scalar_one()
    return result


async def get_user_by_email(db: AsyncSession, email: str):
    """ Возвращает данные юзера по email.  """
    query = select(User).filter(User.email == email)
    result = await db.execute(query)
    await db.commit()
    return result.scalars().first()


async def create_user(db: AsyncSession, user):
    """ Создаёт запись юзера в БД.  """
    hashed_password = CryptContext(schemes=["bcrypt"], deprecated="auto").hash(user.password)
    db_user = User(**user.dict(exclude={"password"}), hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def delete_user(db: AsyncSession, user_id: int):
    """ Удаляет запись юзера из БД.  """
    query = select(User).filter(User.id == user_id)
    user = await db.execute(query)
    user = user.scalars().first()
    if user:
        await db.delete(user)
        await db.commit()
        return user
    else:
        return None
