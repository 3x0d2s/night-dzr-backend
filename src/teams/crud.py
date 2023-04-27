from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.teams.models import Team


async def get_team_data(db: AsyncSession, team_id: int):
    """ Возвращает данные команды.  """
    query = select(Team).filter(Team.id == team_id)
    result = await db.execute(query)
    return result.scalars().first()


async def create_team(db: AsyncSession, team_data):
    """ Создаёт запись команды в БД.  """
    db_team = Team(**team_data.dict())
    db.add(db_team)
    await db.commit()
    await db.refresh(db_team)
    return db_team
