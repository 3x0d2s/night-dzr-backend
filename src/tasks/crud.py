from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.tasks.models import Task
from src.auth.models import User


async def get_task_data(db: AsyncSession, task_id: int):
    """ Возвращает данные загадки.  """
    query = select(Task).filter(Task.id == task_id).options(selectinload(Task.user))
    result = await db.execute(query)
    return result.scalars().first()


async def create_task(db: AsyncSession, task_data, owner_id):
    """ Создаёт запись загадки в БД.  """
    db_task = Task(**task_data.dict(), owner_id=owner_id)
    db.add(db_task)
    await db.commit()
    await db.refresh(db_task)
    return db_task


async def delete_task(db: AsyncSession, task: Task):
    """ Удаляет запись команды из БД.  """
    await db.delete(task)
    await db.commit()
    return task


async def update_task(db: AsyncSession, task: Task, update_data: dict):
    """ Обновляет информация о команде. """
    for key, value in update_data.items():
        setattr(task, key, value)
    await db.commit()
    return task


async def get_user_data(db: AsyncSession, user_id: int) -> User:
    """ Возвращает данные пользователя вместе с созданными им загадками.  """
    query = select(User).filter(User.id == user_id).options(selectinload(User.tasks))
    result = await db.execute(query)
    return result.scalars().first()
