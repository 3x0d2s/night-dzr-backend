from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from src.games.models import Game
from src.games.utils import GamesTaskNotFound, GamesTeamNotFound
from src.auth.models import User
from src.tasks.models import Task
from src.teams.models import Team


async def get_game_data(db: AsyncSession, game_id: int):
    """ Возвращает данные загадки.  """
    query = select(Game).filter(Game.id == game_id).options(selectinload(Game.user))
    result = await db.execute(query)
    return result.scalars().first()


async def get_game_data_with_tasks(db: AsyncSession, game_id: int):
    """ Возвращает данные загадки.  """
    query = select(Game).filter(Game.id == game_id).options(selectinload(Game.user), selectinload(Game.tasks))
    result = await db.execute(query)
    return result.scalars().first()


async def add_task_to_game(db: AsyncSession, game: Game, task_id: int):
    """ Добавляет загадку в игру. """
    query = select(Task).filter(Task.id == task_id)
    result = await db.execute(query)
    task = result.scalars().first()
    game.tasks.append(task)
    await db.commit()


async def remove_task_from_game(db: AsyncSession, game: Game, task_id: int):
    """ Удаляет загадку из игры. """
    flag = False
    for games_task in game.tasks:
        if games_task.id == task_id:
            game.tasks.remove(games_task)
            flag = True
    if not flag:
        raise GamesTaskNotFound
    await db.commit()


async def get_game_data_with_teams(db: AsyncSession, game_id: int):
    """ Возвращает данные загадки.  """
    query = select(Game).filter(Game.id == game_id).options(selectinload(Game.user), selectinload(Game.teams))
    result = await db.execute(query)
    return result.scalars().first()


async def add_team_to_game(db: AsyncSession, game: Game, team_id: int):
    """ Добавляет команду в игру. """
    query = select(Team).filter(Team.id == team_id)
    result = await db.execute(query)
    team = result.scalars().first()
    game.teams.append(team)
    await db.commit()


async def remove_team_from_game(db: AsyncSession, game: Game, team_id: int):
    """ Удаляет команду из игры. """
    flag = False
    for games_team in game.teams:
        if games_team.id == team_id:
            game.teams.remove(games_team)
            flag = True
    if not flag:
        raise GamesTeamNotFound
    await db.commit()


async def add_team_to_game(db: AsyncSession, game: Game, team_id: int):
    """ Добавляет загадку в игру. """
    query = select(Team).filter(Team.id == team_id)
    result = await db.execute(query)
    team = result.scalars().first()
    game.teams.append(team)
    await db.commit()


async def create_game(db: AsyncSession, game_data, owner_id):
    """ Создаёт запись загадки в БД.  """
    db_game = Game(**game_data.dict(), owner_id=owner_id)
    db.add(db_game)
    await db.commit()
    await db.refresh(db_game)
    return db_game


async def delete_game(db: AsyncSession, game: Game):
    """ Удаляет запись игры из БД.  """
    await db.delete(game)
    await db.commit()
    return game


async def update_game(db: AsyncSession, game: Game, update_data: dict):
    """ Обновляет информация об игре. """
    for key, value in update_data.items():
        setattr(game, key, value)
    await db.commit()
    return game


async def get_user_data(db: AsyncSession, user_id: int) -> User:
    """ Возвращает данные пользователя вместе с созданными им играми.  """
    query = select(User).filter(User.id == user_id).options(selectinload(User.games))  # TODO: .limit(10)
    result = await db.execute(query)
    return result.scalars().first()
