from sqlalchemy import select, exists
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.teams.models import Team
from src.auth.models import User
from src.teams.utils import TeamsUserNotFound


async def get_team_data(db: AsyncSession, team_id: int):
    """ Возвращает данные команды.  """
    query = select(Team).filter(Team.id == team_id).options(selectinload(Team.users))
    result = await db.execute(query)
    return result.scalars().first()


async def check_team_name_in_db(db: AsyncSession, team_name: str):
    """ Проверяет наличие переданного названия команды в базе данных.  """
    query = exists(1).select_from(Team).where(func.lower(Team.name) == func.lower(team_name)).select()
    curr = await db.execute(query)
    return curr.scalar_one()


async def create_team(db: AsyncSession, team_data, owner_id):
    """ Создаёт запись команды в БД.  """
    db_team = Team(**team_data.dict(), owner_id=owner_id)
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team


async def delete_team(db: AsyncSession, team: Team):
    """ Удаляет запись команды из БД.  """
    await db.delete(team)
    await db.commit()
    return team


async def update_team(db: AsyncSession, team: Team, update_data: dict):
    for key, value in update_data.items():
        setattr(team, key, value)
    await db.commit()
    return team


async def add_user_to_team(db: AsyncSession, team: Team, user_id: int):
    query = select(User).filter(User.id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()
    team.users.append(user)
    await db.commit()


async def remove_user_from_team(db: AsyncSession, team: Team, user_id: int):
    flag = False
    for team_user in team.users:
        if team_user.id == user_id:
            team.users.remove(team_user)
            flag = True
    if not flag:
        raise TeamsUserNotFound
    await db.commit()
