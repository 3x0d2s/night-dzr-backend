from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.tasks.models import Task
from src.auth.models import User


class TasksCrud:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    async def get_task_data(self, task_id: int):
        """ Возвращает данные загадки.  """
        query = select(Task).filter(Task.id == task_id).options(selectinload(Task.user))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def create_task(self, task_data, owner_id):
        """ Создаёт запись загадки в БД.  """
        db_task = Task(**task_data.dict(), owner_id=owner_id)
        self.db.add(db_task)
        return db_task

    async def delete_task(self, task: Task):
        """ Удаляет запись команды из БД.  """
        await self.db.delete(task)
        return task

    async def update_task(self, task: Task, update_data: dict):
        """ Обновляет информация о команде. """
        for key, value in update_data.items():
            setattr(task, key, value)
        return task

    async def get_user_data(self, user_id: int) -> User:
        """ Возвращает данные пользователя вместе с созданными им загадками.  """
        query = select(User).filter(User.id == user_id).options(selectinload(User.tasks))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def commit(self):
        await self.db.commit()

    async def refresh(self, instance: object):
        await self.db.refresh(instance)
