from sqlalchemy import select, exists
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.teams.models import Team
from src.auth.models import User
from src.teams.utils import TeamsUserNotFound


class TeamsCrud:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session
        
    async def get_team_data(self, team_id: int):
        """ Возвращает данные команды.  """
        query = select(Team).filter(Team.id == team_id).options(selectinload(Team.users))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def check_team_name_in_db(self, team_name: str):
        """ Проверяет наличие переданного названия команды в базе данных.  """
        query = exists(1).select_from(Team).where(func.lower(Team.name) == func.lower(team_name)).select()
        curr = await self.db.execute(query)
        return curr.scalar_one()
    
    async def create_team(self, team_data, owner_id):
        """ Создаёт запись команды в БД.  """
        db_team = Team(**team_data.dict(), owner_id=owner_id)
        self.db.add(db_team)
        return db_team

    async def delete_team(self, team: Team):
        """ Удаляет запись команды из БД.  """
        await self.db.delete(team)
        return team
    
    async def update_team(self, team: Team, update_data: dict):
        """ Обновляет информация о команде. """
        for key, value in update_data.items():
            setattr(team, key, value)
        await self.db.commit()
        return team

    async def add_user_to_team(self, team: Team, user_id: int):
        """ Добавляет пользователя в команду.  """
        query = select(User).filter(User.id == user_id)
        result = await self.db.execute(query)
        user = result.scalars().first()
        team.users.append(user)
    
    async def remove_user_from_team(self, team: Team, user_id: int):
        """ Удаляет пользователя из команды. """
        flag = False
        for team_user in team.users:
            if team_user.id == user_id:
                team.users.remove(team_user)
                flag = True
        if not flag:
            raise TeamsUserNotFound
    
    async def get_user_data(self, user_id: int) -> User:
        """ Возвращает данные пользователя вместе с командой.  """
        query = select(User).filter(User.id == user_id).options(selectinload(User.team))
        result = await self.db.execute(query)
        return result.scalars().first()

    async def get_user_data_by_email(self, user_email: str) -> User:
        """ Возвращает данные пользователя вместе с командой.  """
        query = select(User).filter(User.email == user_email).options(selectinload(User.team))
        result = await self.db.execute(query)
        return result.scalars().first()
    
    async def commit(self):
        await self.db.commit()

    async def refresh(self, instance: object):
        await self.db.refresh(instance)
